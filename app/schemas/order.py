import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.order import OrderStatus


class OrderItemIn(BaseModel):
    product_slug: str
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    # customer_name NO va aqui: se toma del nombre de Google en el JWT (login obligatorio).
    customer_phone: str
    delivery_address: str
    department: str
    city: str
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
    created_at: datetime
    items: list[OrderItemOut]


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
