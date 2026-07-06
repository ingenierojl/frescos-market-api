from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(80))
    unit: Mapped[str] = mapped_column(String(30))  # "por libra", "por unidad", "atado"...
    price: Mapped[int] = mapped_column(Integer)  # COP, sin decimales
    category: Mapped[str] = mapped_column(String(30))  # "hortalizas" | "frutas"
    photo_url: Mapped[str] = mapped_column(String(300))
    stock: Mapped[int | None] = mapped_column(Integer, nullable=True)  # null = sin control de stock
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
