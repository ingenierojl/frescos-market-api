import httpx

from app.core.config import settings


def format_cop(amount: int) -> str:
    return f"{amount:,}".replace(",", ".")


async def send_telegram_notification(chat_id: str | None, message: str) -> None:
    """Best-effort: si falla (bot mal configurado, sin internet, etc.) no debe romper el pedido."""
    if not settings.telegram_bot_token or not chat_id:
        return

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(url, json={"chat_id": chat_id, "text": message})
            if response.status_code != 200:
                print(f"[telegram] error {response.status_code}: {response.text}")
    except Exception as exc:  # noqa: BLE001 - notificacion best-effort, nunca debe tumbar el pedido
        print(f"[telegram] excepcion enviando notificacion: {exc}")
