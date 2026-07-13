import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import CurrentUser
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.profile import Profile
from app.schemas.order import OrderCreate
from app.services.settings_service import get_or_create_settings
from app.services.telegram_service import format_cop, send_telegram_notification


async def _save_profile(db: AsyncSession, user_id: str, payload: OrderCreate) -> None:
    """Recuerda telefono/direccion/ciudad del usuario para no volver a pedirlos despues."""
    profile = await db.get(Profile, user_id)
    if profile is None:
        profile = Profile(user_id=user_id)
        db.add(profile)
    profile.phone = payload.customer_phone
    profile.address = payload.delivery_address
    profile.department = payload.department
    profile.city = payload.city


async def create_order(db: AsyncSession, payload: OrderCreate, current_user: CurrentUser | None) -> Order:
    slugs = [item.product_slug for item in payload.items]
    result = await db.execute(select(Product).where(Product.slug.in_(slugs)))
    products_by_slug = {p.slug: p for p in result.scalars().all()}

    missing = set(slugs) - products_by_slug.keys()
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Productos inexistentes: {sorted(missing)}",
        )

    order_items: list[OrderItem] = []
    total = 0
    for item in payload.items:
        product = products_by_slug[item.product_slug]
        if product.stock is not None and product.stock < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Sin stock suficiente de {product.name}",
            )
        subtotal = product.price * item.quantity
        total += subtotal
        order_items.append(
            OrderItem(
                product_id=product.id,
                quantity=item.quantity,
                unit_price=product.price,
                subtotal=subtotal,
            )
        )
        if product.stock is not None:
            product.stock -= item.quantity

    if current_user is None and not (payload.customer_name and payload.customer_name.strip()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Falta el nombre del cliente para un pedido de invitado",
        )

    order = Order(
        user_id=uuid.UUID(current_user.id) if current_user else None,
        total=total,
        customer_name=(
            current_user.full_name or current_user.email or "Cliente"
            if current_user
            else payload.customer_name.strip()
        ),
        customer_phone=payload.customer_phone,
        delivery_address=payload.delivery_address,
        department=payload.department,
        city=payload.city,
        payment_method=payload.payment_method,
        channel=payload.channel,
        items=order_items,
    )
    db.add(order)
    if current_user:
        await _save_profile(db, current_user.id, payload)
    await db.commit()
    await db.refresh(order, attribute_names=["items"])

    settings_row = await get_or_create_settings(db)
    await send_telegram_notification(
        settings_row.telegram_chat_id,
        f"🛒 Pedido nuevo de {order.customer_name}, ${format_cop(order.total)}\n"
        f"{order.delivery_address}, {order.city} ({order.department})\n"
        f"Pago: {'transferencia' if order.payment_method == 'transferencia' else 'efectivo'}",
    )

    return order
