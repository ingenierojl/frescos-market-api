import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderItem
from app.models.product import Product
from app.schemas.order import OrderCreate


async def create_order(db: AsyncSession, payload: OrderCreate, user_id: uuid.UUID | None) -> Order:
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

    order = Order(
        user_id=user_id,
        total=total,
        customer_name=payload.customer_name,
        customer_phone=payload.customer_phone,
        delivery_address=payload.delivery_address,
        items=order_items,
    )
    db.add(order)
    await db.commit()
    await db.refresh(order, attribute_names=["items"])
    return order
