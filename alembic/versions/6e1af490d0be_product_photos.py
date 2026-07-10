"""fotos adicionales de producto (hasta 3, para el slider)

Revision ID: 6e1af490d0be
Revises: c63e6e3f473c
Create Date: 2026-07-10 05:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '6e1af490d0be'
down_revision: Union[str, None] = 'c63e6e3f473c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'product_photos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('photo_url', sa.String(length=300), nullable=False),
        sa.Column('sort_order', sa.Integer(), server_default='0', nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_product_photos_product_id', 'product_photos', ['product_id'])


def downgrade() -> None:
    op.drop_index('ix_product_photos_product_id', table_name='product_photos')
    op.drop_table('product_photos')
