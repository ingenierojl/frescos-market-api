import uuid

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.api.v1.deps import CurrentAdmin, CurrentTeam, DbSession
from app.models.catalog_option import CatalogOption
from app.models.order import Order
from app.models.payment_option import PaymentOption
from app.models.product import Product
from app.schemas.catalog_option import CatalogOptionCreate, CatalogOptionOut
from app.schemas.order import OrderOut, OrderStatusUpdate
from app.schemas.payment_option import PaymentOptionCreate, PaymentOptionOut, PaymentOptionUpdate
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate
from app.schemas.settings import AppSettingsOut, AppSettingsUpdate
from app.services.settings_service import get_or_create_settings

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/orders", response_model=list[OrderOut])
async def list_all_orders(db: DbSession, _team: CurrentTeam):
    """Ve todos los pedidos: admin y despachador (para saber que entregar)."""
    query = select(Order).options(selectinload(Order.items)).order_by(Order.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.patch("/orders/{order_id}/status", response_model=OrderOut)
async def update_order_status(
    order_id: uuid.UUID,
    payload: OrderStatusUpdate,
    db: DbSession,
    _team: CurrentTeam,
):
    order = await db.get(Order, order_id, options=[selectinload(Order.items)])
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")

    order.status = payload.status.value
    await db.commit()
    await db.refresh(order, attribute_names=["items"])
    return order


@router.delete("/orders/{order_id}", status_code=204)
async def delete_order(order_id: uuid.UUID, db: DbSession, _admin: CurrentAdmin):
    """Solo admin (el despachador no puede borrar pedidos, solo cambiarles el estado)."""
    order = await db.get(
        Order,
        order_id,
        options=[selectinload(Order.items), selectinload(Order.messages)],
    )
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")

    # items y messages se borran en cascada (delete-orphan del ORM); hay que
    # cargarlos antes (selectinload) porque el cascade corre en Python, no en la DB.
    await db.delete(order)
    await db.commit()


@router.get("/settings", response_model=AppSettingsOut)
async def get_settings(db: DbSession, _admin: CurrentAdmin):
    return await get_or_create_settings(db)


@router.put("/settings", response_model=AppSettingsOut)
async def update_settings(payload: AppSettingsUpdate, db: DbSession, _admin: CurrentAdmin):
    settings_row = await get_or_create_settings(db)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(settings_row, key, value)
    await db.commit()
    await db.refresh(settings_row)
    return settings_row


@router.post("/catalog-options", response_model=CatalogOptionOut, status_code=201)
async def create_catalog_option(payload: CatalogOptionCreate, db: DbSession, _admin: CurrentAdmin):
    value = payload.value.strip()
    existing = await db.execute(
        select(CatalogOption).where(CatalogOption.type == payload.type, CatalogOption.value == value)
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Esa opción ya existe")

    count_result = await db.execute(select(CatalogOption).where(CatalogOption.type == payload.type))
    max_order = len(count_result.scalars().all())

    option = CatalogOption(type=payload.type, value=value, sort_order=max_order)
    db.add(option)
    await db.commit()
    await db.refresh(option)
    return option


@router.delete("/catalog-options/{option_id}", status_code=204)
async def delete_catalog_option(option_id: int, db: DbSession, _admin: CurrentAdmin):
    option = await db.get(CatalogOption, option_id)
    if option is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opción no encontrada")
    await db.delete(option)
    await db.commit()


@router.post("/payment-options", response_model=PaymentOptionOut, status_code=201)
async def create_payment_option(payload: PaymentOptionCreate, db: DbSession, _admin: CurrentAdmin):
    count_result = await db.execute(select(PaymentOption))
    max_order = len(count_result.scalars().all())

    option = PaymentOption(
        label=payload.label.strip(),
        phone_or_account=payload.phone_or_account.strip(),
        qr_image_url=payload.qr_image_url,
        sort_order=max_order,
    )
    db.add(option)
    await db.commit()
    await db.refresh(option)
    return option


@router.put("/payment-options/{option_id}", response_model=PaymentOptionOut)
async def update_payment_option(option_id: int, payload: PaymentOptionUpdate, db: DbSession, _admin: CurrentAdmin):
    option = await db.get(PaymentOption, option_id)
    if option is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opción no encontrada")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(option, key, value)

    await db.commit()
    await db.refresh(option)
    return option


@router.delete("/payment-options/{option_id}", status_code=204)
async def delete_payment_option(option_id: int, db: DbSession, _admin: CurrentAdmin):
    option = await db.get(PaymentOption, option_id)
    if option is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opción no encontrada")
    await db.delete(option)
    await db.commit()


@router.get("/products", response_model=list[ProductOut])
async def list_all_products(db: DbSession, _admin: CurrentAdmin):
    """Como /api/v1/products pero incluye inactivos, para gestionarlos."""
    result = await db.execute(select(Product).order_by(Product.name))
    return result.scalars().all()


@router.post("/products", response_model=ProductOut, status_code=201)
async def create_product(payload: ProductCreate, db: DbSession, _admin: CurrentAdmin):
    existing = await db.execute(select(Product).where(Product.slug == payload.slug))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe un producto con ese slug")

    product = Product(**payload.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


@router.put("/products/{product_id}", response_model=ProductOut)
async def update_product(product_id: int, payload: ProductUpdate, db: DbSession, _admin: CurrentAdmin):
    product = await db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, key, value)

    await db.commit()
    await db.refresh(product)
    return product


@router.delete("/products/{product_id}", status_code=204)
async def delete_product(product_id: int, db: DbSession, _admin: CurrentAdmin):
    product = await db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    await db.delete(product)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar: tiene pedidos asociados. Desactívalo en vez de borrarlo.",
        )
