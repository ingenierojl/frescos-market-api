import httpx

from app.core.config import settings

CHAT_IMAGES_PREFIX = "/storage/v1/object/public/chat-images/"


def _extract_storage_path(image_url: str) -> str | None:
    idx = image_url.find(CHAT_IMAGES_PREFIX)
    if idx == -1:
        return None
    return image_url[idx + len(CHAT_IMAGES_PREFIX):]


async def delete_chat_images(image_urls: list[str]) -> None:
    """Best-effort: borra las fotos del chat en Supabase Storage al eliminar
    un pedido. Si falla (o no hay service_role_key configurada), no debe
    romper el borrado del pedido -- las fotos simplemente quedan huerfanas,
    que es el comportamiento anterior a este cleanup."""
    if not settings.supabase_service_role_key:
        return

    paths = [p for p in (_extract_storage_path(url) for url in image_urls) if p]
    if not paths:
        return

    url = f"{settings.supabase_url.rstrip('/')}/storage/v1/object/chat-images"
    headers = {
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
        "apikey": settings.supabase_service_role_key,
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.request("DELETE", url, headers=headers, json={"prefixes": paths})
            if response.status_code >= 300:
                print(f"[storage] error borrando fotos del chat {response.status_code}: {response.text}")
    except Exception as exc:  # noqa: BLE001 - limpieza best-effort, nunca debe tumbar el borrado del pedido
        print(f"[storage] excepcion borrando fotos del chat: {exc}")
