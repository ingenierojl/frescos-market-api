from fastapi import APIRouter, HTTPException, status

from app.api.v1.deps import CurrentUserRequired, DbSession
from app.models.profile import Profile
from app.schemas.profile import ProfileOut, ProfileUpsert

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def read_current_user(current_user: CurrentUserRequired):
    return {"id": current_user.id, "email": current_user.email, "full_name": current_user.full_name}


@router.get("/me/profile", response_model=ProfileOut)
async def get_my_profile(db: DbSession, current_user: CurrentUserRequired):
    profile = await db.get(Profile, current_user.id)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sin perfil guardado todavía")
    return profile


@router.put("/me/profile", response_model=ProfileOut)
async def upsert_my_profile(payload: ProfileUpsert, db: DbSession, current_user: CurrentUserRequired):
    profile = await db.get(Profile, current_user.id)
    if profile is None:
        profile = Profile(user_id=current_user.id)
        db.add(profile)
    profile.phone = payload.phone
    profile.address = payload.address
    profile.department = payload.department
    profile.city = payload.city
    await db.commit()
    await db.refresh(profile)
    return profile
