
from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DatabaseSession
from app.models.scan import Scan

router = APIRouter(prefix="/history", tags=["Scan History"])


# Get scan history
@router.get("/")
def get_scan_history(
    db: DatabaseSession,
    current_user: CurrentUser,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    scans = (
        db.query(Scan)
        .filter(Scan.user_id == current_user.id)
        .order_by(Scan.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "items": [
            {
                "id": scan.id,
                "url": scan.url,
                "risk_score": scan.risk_score,
                "risk_level": scan.risk_level,
                "explanation": scan.explanation,
                "created_at": scan.created_at,
            }
            for scan in scans
        ],
        "limit": limit,
        "offset": offset,
    }


# Clear all scan history for the logged-in user
@router.delete("/")
def clear_scan_history(
    db: DatabaseSession,
    current_user: CurrentUser,
):
    try:
        deleted_count = (
            db.query(Scan)
            .filter(Scan.user_id == current_user.id)
            .delete(synchronize_session=False)
        )

        db.commit()

        return {
            "message": "Scan history cleared successfully!",
            "deleted_count": deleted_count,
        }

    except Exception:
        db.rollback()
        raise
