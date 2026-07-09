"""payment_method en orders + tabla payment_options (Nequi/Daviplata/etc.)

Revision ID: bde58a1f2faf
Revises: c8f3d6e2a115
Create Date: 2026-07-08 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'bde58a1f2faf'
down_revision: Union[str, None] = 'c8f3d6e2a115'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'orders',
        sa.Column('payment_method', sa.String(length=20), nullable=False, server_default='efectivo'),
    )

    op.create_table(
        'payment_options',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('label', sa.String(length=60), nullable=False),
        sa.Column('phone_or_account', sa.String(length=60), nullable=False),
        sa.Column('qr_image_url', sa.String(length=300), nullable=True),
        sa.Column('sort_order', sa.Integer(), server_default='0', nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('payment_options')
    op.drop_column('orders', 'payment_method')
