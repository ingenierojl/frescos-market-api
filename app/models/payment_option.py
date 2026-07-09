from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PaymentOption(Base):
    """Destinos de transferencia (Nequi, Daviplata, cuenta bancaria...) que se
    muestran al cliente cuando elige pagar por transferencia. Editable desde
    el panel de admin, igual que catalog_options."""

    __tablename__ = "payment_options"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    label: Mapped[str] = mapped_column(String(60))  # ej: "Nequi", "Daviplata", "Bancolombia"
    phone_or_account: Mapped[str] = mapped_column(String(60))  # numero de celular o numero de cuenta
    qr_image_url: Mapped[str | None] = mapped_column(String(300), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
