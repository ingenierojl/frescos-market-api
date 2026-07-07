import uuid

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.api.v1.deps import CurrentAdmin, DbSession
from app.models.order import Order
from app.models.product import Product
from app.schemas.order import OrderOut, OrderStatusUpdate
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/orders", response_model=list[OrderOut])
async def list_all_orders(db: DbSession, _admin: CurrentAdmin):
    query = select(Order).options(selectinload(Order.items)).order_by(Order.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.patch("/orders/{order_id}/status", response_model=OrderOut)
async def update_order_status(
    order_id: uuid.UUID,
    payload: OrderStatusUpdate,
    db: DbSession,
    _admin: CurrentAdmin,
):
    order = await db.get(Order, order_id, options=[selectinload(Order.items)])
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")

    order.status = payload.status.value
    await db.commit()
    await db.refresh(order, attribute_names=["items"])
    return order


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
