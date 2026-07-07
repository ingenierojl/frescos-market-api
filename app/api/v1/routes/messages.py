import uuid

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.v1.deps import CurrentUserOptional, DbSession, is_admin_email, is_dispatcher_email
from app.models.order import Order, OrderMessage
from app.schemas.message import MessageCreate, MessageOut

router = APIRouter(prefix="/orders", tags=["messages"])


async def _get_order_with_access_check(db: DbSession, order_id: uuid.UUID, current_user):
    order = await db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")

    is_team = current_user and (is_admin_email(current_user.email) or is_dispatcher_email(current_user.email))
    is_owner = (
        current_user is not None and order.user_id is not None and str(order.user_id) == current_user.id
    )
    # Los pedidos de invitado (sin user_id) no tienen dueño verificable por login:
    # el propio order_id (un UUID dificil de adivinar) hace de "llave" del chat.
    is_guest_order = order.user_id is None

    if not (is_team or is_owner or is_guest_order):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")

    return order, is_team


@router.get("/{order_id}/messages", response_model=list[MessageOut])
async def list_messages(order_id: uuid.UUID, db: DbSession, current_user: CurrentUserOptional):
    await _get_order_with_access_check(db, order_id, current_user)
    result = await db.execute(
        select(OrderMessage).where(OrderMessage.order_id == order_id).order_by(OrderMessage.created_at)
    )
    return result.scalars().all()


@router.post("/{order_id}/messages", response_model=MessageOut, status_code=201)
async def create_message(
    order_id: uuid.UUID,
    payload: MessageCreate,
    db: DbSession,
    current_user: CurrentUserOptional,
):
    _order, is_team = await _get_order_with_access_check(db, order_id, current_user)

    message = OrderMessage(
        order_id=order_id,
        sender_role="team" if is_team else "customer",
        sender_email=current_user.email if current_user else None,
        body=payload.body,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message
