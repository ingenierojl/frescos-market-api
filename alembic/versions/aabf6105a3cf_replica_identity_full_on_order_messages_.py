"""replica identity full on order_messages for realtime

Revision ID: aabf6105a3cf
Revises: eeddf2f43cef
Create Date: 2026-07-07 15:19:11.866371

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aabf6105a3cf'
down_revision: Union[str, None] = 'eeddf2f43cef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Supabase Realtime + RLS necesita la fila completa para evaluar la policy
    # de cada evento y decidir a quien entregarlo. Con la identidad por defecto
    # (solo la PK) los eventos se filtran y no llegan al cliente. Solo afecta el
    # WAL/replicacion; no cambia el comportamiento de la app ni de la API.
    op.execute("ALTER TABLE order_messages REPLICA IDENTITY FULL")


def downgrade() -> None:
    op.execute("ALTER TABLE order_messages REPLICA IDENTITY DEFAULT")
