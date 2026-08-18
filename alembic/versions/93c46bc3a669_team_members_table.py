"""team_members table, reemplaza TEAM_EMAILS hardcodeado en RLS

Revision ID: 93c46bc3a669
Revises: 23530034ea8c
Create Date: 2026-08-18 00:27:49.788357

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '93c46bc3a669'
down_revision: Union[str, None] = '23530034ea8c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Los mismos dos correos que ya estaban hardcodeados en la migracion
# eeddf2f43cef (TEAM_EMAILS) -- se siembran aca para que nadie pierda ni
# gane acceso con este cambio.
SEED_TEAM = [
    ("ingenierorojas87@gmail.com", "admin"),
    ("georgereds02@gmail.com", "dispatcher"),
]

OLD_TEAM_EMAILS = "('ingenierorojas87@gmail.com', 'georgereds02@gmail.com')"


def upgrade() -> None:
    op.create_table(
        "team_members",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_team_members_email", "team_members", ["email"])

    # RLS activado y SIN policies: nadie puede leerla desde el navegador
    # (ni anon ni logueado) -- solo el backend, que usa el rol con
    # privilegios que bypassea RLS por completo.
    op.execute("ALTER TABLE team_members ENABLE ROW LEVEL SECURITY")

    for email, role in SEED_TEAM:
        op.execute(
            sa.text("INSERT INTO team_members (email, role) VALUES (:email, :role)").bindparams(
                email=email, role=role
            )
        )

    # Reescribe las dos policies de eeddf2f43cef para que consulten esta
    # tabla en vez de la lista hardcodeada -- una sola fuente de verdad
    # para el backend (FastAPI) y para Realtime (RLS de Supabase).
    op.execute("DROP POLICY IF EXISTS select_own_or_team_orders ON orders")
    op.execute("""
        CREATE POLICY select_own_or_team_orders ON orders
        FOR SELECT
        USING (
            EXISTS (SELECT 1 FROM team_members WHERE team_members.email = auth.jwt() ->> 'email')
            OR user_id = auth.uid()
        )
    """)

    op.execute("DROP POLICY IF EXISTS select_own_or_team_messages ON order_messages")
    op.execute("""
        CREATE POLICY select_own_or_team_messages ON order_messages
        FOR SELECT
        USING (
            EXISTS (SELECT 1 FROM team_members WHERE team_members.email = auth.jwt() ->> 'email')
            OR EXISTS (
                SELECT 1 FROM orders
                WHERE orders.id = order_messages.order_id
                AND orders.user_id = auth.uid()
            )
        )
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS select_own_or_team_messages ON order_messages")
    op.execute(f"""
        CREATE POLICY select_own_or_team_messages ON order_messages
        FOR SELECT
        USING (
            auth.jwt() ->> 'email' IN {OLD_TEAM_EMAILS}
            OR EXISTS (
                SELECT 1 FROM orders
                WHERE orders.id = order_messages.order_id
                AND orders.user_id = auth.uid()
            )
        )
    """)

    op.execute("DROP POLICY IF EXISTS select_own_or_team_orders ON orders")
    op.execute(f"""
        CREATE POLICY select_own_or_team_orders ON orders
        FOR SELECT
        USING (
            auth.jwt() ->> 'email' IN {OLD_TEAM_EMAILS}
            OR user_id = auth.uid()
        )
    """)

    op.drop_index("ix_team_members_email", table_name="team_members")
    op.drop_table("team_members")
