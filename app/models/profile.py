from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Profile(Base):
    """Datos de entrega recordados por usuario (telefono/direccion/ciudad),
    para no volver a pedirlos en cada pedido. user_id = auth.users.id de Supabase
    (no hay FK real: esa tabla vive en el esquema "auth", fuera de nuestro alcance)."""

    __tablename__ = "profiles"

    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    phone: Mapped[str] = mapped_column(String(30))
    address: Mapped[str] = mapped_column(String(300))
    department: Mapped[str] = mapped_column(String(60))
    city: Mapped[str] = mapped_column(String(60))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
