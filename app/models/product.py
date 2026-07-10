from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

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

    photos: Mapped[list["ProductPhoto"]] = relationship(
        back_populates="product", cascade="all, delete-orphan", order_by="ProductPhoto.sort_order"
    )


class ProductPhoto(Base):
    """Fotos adicionales de un producto (maximo 3), ademas de la foto principal
    (Product.photo_url). Se muestran como slider al hacer click en la tarjeta."""

    __tablename__ = "product_photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), index=True)
    photo_url: Mapped[str] = mapped_column(String(300))
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    product: Mapped["Product"] = relationship(back_populates="photos")
