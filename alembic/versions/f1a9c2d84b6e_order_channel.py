"""canal del pedido: google o whatsapp

Revision ID: f1a9c2d84b6e
Revises: 6e1af490d0be
Create Date: 2026-07-12 19:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f1a9c2d84b6e'
down_revision: Union[str, None] = '6e1af490d0be'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('orders', sa.Column('channel', sa.String(length=20), server_default='google', nullable=False))


def downgrade() -> None:
    op.drop_column('orders', 'channel')
