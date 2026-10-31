
from fastapi import APIRouter

from app.api.deps import CurrentUser, DatabaseSession
from app.services.analytics_service import get_user_analytics

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/")
def analytics(
    db: DatabaseSession,
    current_user: CurrentUser,
):
    return get_user_analytics(db, current_user.id)
