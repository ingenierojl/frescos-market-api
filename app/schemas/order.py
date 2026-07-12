import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.order import OrderStatus


class OrderItemIn(BaseModel):
    product_slug: str
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    # customer_name solo se usa para pedidos de invitado (sin login); si hay sesion,
    # el nombre se toma del JWT de Google y este campo se ignora.
    customer_name: str | None = None
    customer_phone: str
    delivery_address: str
    department: str
    city: str
    payment_method: str = Field(pattern="^(efectivo|transferencia)$", default="efectivo")
    items: list[OrderItemIn]


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    quantity: int
    unit_price: int
    subtotal: int


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: str
    total: int
    customer_name: str
    customer_phone: str
    delivery_address: str
    department: str
    city: str
    payment_method: str
    created_at: datetime
    items: list[OrderItemOut]


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
