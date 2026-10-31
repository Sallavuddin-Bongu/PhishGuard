
from fastapi import APIRouter

from app.api.deps import CurrentUser, DatabaseSession
from app.models.user import User
from app.schemas.user import UserProfileResponse, UserProfileUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserProfileResponse)
def get_profile(current_user: CurrentUser):
    return current_user


@router.patch("/me", response_model=UserProfileResponse)
def update_profile(
    data: UserProfileUpdate,
    db: DatabaseSession,
    current_user: CurrentUser,
):
    current_user.name = data.name.strip()
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return current_user
