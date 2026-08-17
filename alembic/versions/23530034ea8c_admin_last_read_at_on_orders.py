"""admin_last_read_at on orders

Revision ID: 23530034ea8c
Revises: f1a9c2d84b6e
Create Date: 2026-08-17 14:18:07.776202

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '23530034ea8c'
down_revision: Union[str, None] = 'f1a9c2d84b6e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # NULL = el equipo (admin/despachador) nunca ha visto el chat de este
    # pedido -- todos sus mensajes de cliente cuentan como no leidos.
    op.add_column('orders', sa.Column('admin_last_read_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('orders', 'admin_last_read_at')
