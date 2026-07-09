from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AppSettings(Base):
    """Fila unica (id=1) con configuracion editable desde el panel de admin."""

    __tablename__ = "app_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_chat_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    whatsapp_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    # Datos para el schema.org LocalBusiness (SEO). Todos opcionales: si
    # quedan vacios, el campo simplemente se omite del JSON-LD.
    business_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    street_address: Mapped[str | None] = mapped_column(String(200), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
