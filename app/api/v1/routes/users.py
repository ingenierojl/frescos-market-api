from fastapi import APIRouter

from app.api.v1.deps import CurrentUserRequired

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def read_current_user(current_user: CurrentUserRequired):
    return {"id": current_user.id, "email": current_user.email}
