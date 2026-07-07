from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import CurrentUser, decode_supabase_jwt
from app.db.session import get_db

DbSession = Annotated[AsyncSession, Depends(get_db)]

# auto_error=False para poder distinguir "no vino token" (invitado) de "token invalido"
_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
) -> CurrentUser:
    """Requiere sesion. Usar en endpoints como /orders/me."""
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Falta el header Authorization")
    return decode_supabase_jwt(credentials.credentials)


async def get_current_user_optional(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
) -> CurrentUser | None:
    """Permite invitado. Usar en endpoints como crear pedido sin login."""
    if credentials is None:
        return None
    return decode_supabase_jwt(credentials.credentials)


CurrentUserRequired = Annotated[CurrentUser, Depends(get_current_user)]
CurrentUserOptional = Annotated[CurrentUser | None, Depends(get_current_user_optional)]


async def get_current_admin(current_user: CurrentUserRequired) -> CurrentUser:
    """Requiere sesion Y que el email coincida con ADMIN_EMAIL. Usar en /admin/*."""
    is_admin = bool(settings.admin_email) and (
        current_user.email or ""
    ).strip().lower() == settings.admin_email.strip().lower()
    if not is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    return current_user


CurrentAdmin = Annotated[CurrentUser, Depends(get_current_admin)]
