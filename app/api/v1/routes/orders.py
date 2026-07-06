import uuid

from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.v1.deps import CurrentUserOptional, CurrentUserRequired, DbSession
from app.models.order import Order
from app.schemas.order import OrderCreate, OrderOut
from app.services.order_service import create_order

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderOut, status_code=201)
async def create_order_endpoint(
    payload: OrderCreate,
    db: DbSession,
    current_user: CurrentUserOptional,
):
    user_id = uuid.UUID(current_user.id) if current_user else None
    return await create_order(db, payload, user_id)


@router.get("/me", response_model=list[OrderOut])
async def my_orders(db: DbSession, current_user: CurrentUserRequired):
    query = (
        select(Order)
        .where(Order.user_id == uuid.UUID(current_user.id))
        .options(selectinload(Order.items))
        .order_by(Order.created_at.desc())
    )
    result = await db.execute(query)
    return result.scalars().all()
