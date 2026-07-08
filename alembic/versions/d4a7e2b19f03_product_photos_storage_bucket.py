"""product-photos storage bucket + RLS (admin sube, publico ve)

Revision ID: d4a7e2b19f03
Revises: b3f1c9d2a6e4
Create Date: 2026-07-08 05:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.core.config import settings

# revision identifiers, used by Alembic.
revision: str = 'd4a7e2b19f03'
down_revision: Union[str, None] = 'b3f1c9d2a6e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

BUCKET_ID = "product-photos"


def upgrade() -> None:
    # Bucket publico: las fotos se sirven por URL publica sin necesitar RLS de lectura.
    # 8MB es de sobra para una foto de celular ya comprimida por el navegador/OS.
    op.execute(
        sa.text(
            """
            insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
            values (:bucket_id, :bucket_id, true, 8388608, array['image/jpeg', 'image/png', 'image/webp'])
            on conflict (id) do nothing
            """
        ).bindparams(bucket_id=BUCKET_ID)
    )

    # Solo el admin (por email, igual que el resto de la app) puede subir/editar/borrar fotos.
    # El SELECT no necesita policy: el bucket publico sirve los objetos sin pasar por RLS.
    # CREATE POLICY no admite bind params (solo funcionan en SELECT/INSERT/UPDATE/DELETE/VALUES),
    # asi que el email se interpola directo: viene de settings (config del servidor), no de un
    # usuario, y no puede traer comillas simples.
    admin_email = settings.admin_email.replace("'", "")
    op.execute(
        f"""
        create policy "product_photos_admin_insert" on storage.objects
        for insert to authenticated
        with check (bucket_id = '{BUCKET_ID}' and (auth.jwt() ->> 'email') = '{admin_email}')
        """
    )
    op.execute(
        f"""
        create policy "product_photos_admin_update" on storage.objects
        for update to authenticated
        using (bucket_id = '{BUCKET_ID}' and (auth.jwt() ->> 'email') = '{admin_email}')
        """
    )
    op.execute(
        f"""
        create policy "product_photos_admin_delete" on storage.objects
        for delete to authenticated
        using (bucket_id = '{BUCKET_ID}' and (auth.jwt() ->> 'email') = '{admin_email}')
        """
    )


def downgrade() -> None:
    op.execute('drop policy if exists "product_photos_admin_delete" on storage.objects')
    op.execute('drop policy if exists "product_photos_admin_update" on storage.objects')
    op.execute('drop policy if exists "product_photos_admin_insert" on storage.objects')
    op.execute(sa.text("delete from storage.buckets where id = :bucket_id").bindparams(bucket_id=BUCKET_ID))
