import jwt
from fastapi import HTTPException, status

from app.core.config import settings


class CurrentUser:
    def __init__(self, id: str, email: str | None):
        self.id = id
        self.email = email


def decode_supabase_jwt(token: str) -> CurrentUser:
    """Valida el JWT que emite Supabase Auth tras el login (Google u otro proveedor)."""
    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido o expirado",
        ) from exc

    return CurrentUser(id=payload["sub"], email=payload.get("email"))
