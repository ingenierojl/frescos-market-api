import uuid

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.v1.deps import CurrentAdmin, DbSession
from app.models.order import Order
from app.schemas.order import OrderOut, OrderStatusUpdate

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
