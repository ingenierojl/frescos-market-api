"""RLS policies and realtime for chat

Revision ID: eeddf2f43cef
Revises: 324bac806a4a
Create Date: 2026-07-07 01:19:52.303728

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'eeddf2f43cef'
down_revision: Union[str, None] = '324bac806a4a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Emails del equipo (admin/despachador) que pueden ver cualquier pedido/chat.
# Se hardcodean aqui porque las policies de RLS corren dentro de Postgres y
# no tienen forma de leer las variables de entorno de la app FastAPI.
TEAM_EMAILS = "('ingenierorojas87@gmail.com', 'georgereds02@gmail.com')"


def upgrade() -> None:
    # El backend (FastAPI/SQLAlchemy) usa un rol con privilegios que bypassea
    # RLS por completo -- estas policies solo importan para conexiones que
    # vienen directo del navegador con el JWT del usuario (Supabase Realtime).
    op.execute(f"""
        CREATE POLICY select_own_or_team_orders ON orders
        FOR SELECT
        USING (
            auth.jwt() ->> 'email' IN {TEAM_EMAILS}
            OR user_id = auth.uid()
        )
    """)

    op.execute(f"""
        CREATE POLICY select_own_or_team_messages ON order_messages
        FOR SELECT
        USING (
            auth.jwt() ->> 'email' IN {TEAM_EMAILS}
            OR EXISTS (
                SELECT 1 FROM orders
                WHERE orders.id = order_messages.order_id
                AND orders.user_id = auth.uid()
            )
        )
    """)

    # Habilita que Supabase Realtime transmita los INSERTs de esta tabla
    # (el envio de mensajes sigue pasando por nuestra API, esto solo es
    # para que el frontend pueda "escuchar" cambios sin hacer polling).
    op.execute("ALTER PUBLICATION supabase_realtime ADD TABLE order_messages")


def downgrade() -> None:
    op.execute("ALTER PUBLICATION supabase_realtime DROP TABLE order_messages")
    op.execute("DROP POLICY IF EXISTS select_own_or_team_messages ON order_messages")
    op.execute("DROP POLICY IF EXISTS select_own_or_team_orders ON orders")
