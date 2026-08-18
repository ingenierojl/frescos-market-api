import enum
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TeamRole(str, enum.Enum):
    admin = "admin"
    dispatcher = "dispatcher"


class TeamMember(Base):
    """Quien tiene acceso al panel de administracion. Reemplaza los antiguos
    ADMIN_EMAIL/DISPATCHER_EMAIL de una sola cuenta cada uno -- ahora puede
    haber varios de cada rol, consultados aca en vez de en variables de
    entorno. Las policies de RLS de orders/order_messages consultan esta
    misma tabla, para no tener dos listas separadas que se puedan desalinear."""

    __tablename__ = "team_members"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    role: Mapped[str] = mapped_column(String(20))  # "admin" | "dispatcher" (TeamRole)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
