"""catalog_options (unidad/categoria/depto/ciudad editables) + whatsapp_number

Revision ID: c8f3d6e2a115
Revises: d4a7e2b19f03
Create Date: 2026-07-08 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c8f3d6e2a115'
down_revision: Union[str, None] = 'd4a7e2b19f03'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Mismos valores que antes estaban fijos en el HTML/JS del frontend, para no
# perder nada al migrar: se siembran como fila inicial, editable desde ya.
SEED_OPTIONS = [
    ("unit", "por libra"), ("unit", "por kilo"), ("unit", "por unidad"),
    ("unit", "atado"), ("unit", "bandeja"), ("unit", "canasta"),
    ("category", "hortalizas"), ("category", "frutas"),
    ("department", "Cundinamarca"),
    ("city", "Fusagasugá"), ("city", "Tocaima"),
]


def upgrade() -> None:
    op.create_table(
        'catalog_options',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=20), nullable=False),
        sa.Column('value', sa.String(length=60), nullable=False),
        sa.Column('sort_order', sa.Integer(), server_default='0', nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('type', 'value', name='uq_catalog_option_type_value'),
    )
    op.create_index('ix_catalog_options_type', 'catalog_options', ['type'])

    catalog_options = sa.table(
        'catalog_options',
        sa.column('type', sa.String),
        sa.column('value', sa.String),
        sa.column('sort_order', sa.Integer),
    )
    op.bulk_insert(
        catalog_options,
        [{'type': t, 'value': v, 'sort_order': i} for i, (t, v) in enumerate(SEED_OPTIONS)],
    )

    op.add_column('app_settings', sa.Column('whatsapp_number', sa.String(length=20), nullable=True))
    op.execute("UPDATE app_settings SET whatsapp_number = '573008079369' WHERE id = 1")
    op.execute(
        "INSERT INTO app_settings (id, whatsapp_number) VALUES (1, '573008079369') "
        "ON CONFLICT (id) DO NOTHING"
    )


def downgrade() -> None:
    op.drop_column('app_settings', 'whatsapp_number')
    op.drop_index('ix_catalog_options_type', table_name='catalog_options')
    op.drop_table('catalog_options')
