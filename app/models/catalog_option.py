from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CatalogOption(Base):
    """Opciones editables desde el panel de admin para los desplegables del
    catalogo (unidad, categoria) y del formulario de pedido (departamento,
    ciudad). Antes eran listas fijas en el HTML/JS."""

    __tablename__ = "catalog_options"
    __table_args__ = (UniqueConstraint("type", "value", name="uq_catalog_option_type_value"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # unit | category | department | city
    value: Mapped[str] = mapped_column(String(60), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
