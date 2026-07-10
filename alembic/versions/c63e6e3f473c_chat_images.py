"""imagen en el chat de pedidos: image_url en order_messages + bucket chat-images

Revision ID: c63e6e3f473c
Revises: bfd0c23ab4fe
Create Date: 2026-07-09 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c63e6e3f473c'
down_revision: Union[str, None] = 'bfd0c23ab4fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

BUCKET_ID = "chat-images"


def upgrade() -> None:
    op.alter_column('order_messages', 'body', existing_type=sa.String(length=1000), nullable=True)
    op.add_column('order_messages', sa.Column('image_url', sa.String(length=300), nullable=True))

    # Bucket publico igual que product-photos (se sirve por URL publica, sin
    # necesitar policy de SELECT). 8MB de sobra para una foto/captura de celular.
    op.execute(
        sa.text(
            """
            insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
            values (:bucket_id, :bucket_id, true, 8388608, array['image/jpeg', 'image/png', 'image/webp'])
            on conflict (id) do nothing
            """
        ).bindparams(bucket_id=BUCKET_ID)
    )

    # A diferencia de product-photos (solo admin), CUALQUIER usuario logueado
    # puede subir aqui -- un cliente necesita poder mandar la foto de su propio
    # comprobante de pago, no solo el equipo.
    op.execute(
        f"""
        create policy "chat_images_authenticated_insert" on storage.objects
        for insert to authenticated
        with check (bucket_id = '{BUCKET_ID}')
        """
    )
    # Sin policy de update/delete a proposito: una vez enviada, la imagen del
    # chat queda como registro fijo (nadie puede "borrar" evidencia despues).


def downgrade() -> None:
    op.execute('drop policy if exists "chat_images_authenticated_insert" on storage.objects')
    op.execute(sa.text("delete from storage.buckets where id = :bucket_id").bindparams(bucket_id=BUCKET_ID))
    op.drop_column('order_messages', 'image_url')
    op.alter_column('order_messages', 'body', existing_type=sa.String(length=1000), nullable=False)
