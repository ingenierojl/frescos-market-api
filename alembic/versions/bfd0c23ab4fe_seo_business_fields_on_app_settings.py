"""telefono/direccion/codigo postal en app_settings (schema.org SEO)

Revision ID: bfd0c23ab4fe
Revises: bde58a1f2faf
Create Date: 2026-07-09 13:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'bfd0c23ab4fe'
down_revision: Union[str, None] = 'bde58a1f2faf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('app_settings', sa.Column('business_phone', sa.String(length=20), nullable=True))
    op.add_column('app_settings', sa.Column('street_address', sa.String(length=200), nullable=True))
    op.add_column('app_settings', sa.Column('postal_code', sa.String(length=10), nullable=True))


def downgrade() -> None:
    op.drop_column('app_settings', 'postal_code')
    op.drop_column('app_settings', 'street_address')
    op.drop_column('app_settings', 'business_phone')
