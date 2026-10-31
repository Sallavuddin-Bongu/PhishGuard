
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.scan import Scan


def get_user_analytics(db: Session, user_id: int) -> dict:
    total = (
        db.query(func.count(Scan.id))
        .filter(Scan.user_id == user_id)
        .scalar()
        or 0
    )

    risk_counts = (
        db.query(Scan.risk_level, func.count(Scan.id))
        .filter(Scan.user_id == user_id)
        .group_by(Scan.risk_level)
        .all()
    )

    counts = {
        "Low": 0,
        "Medium": 0,
        "High": 0,
    }

    for level, count in risk_counts:
        if level in counts:
            counts[level] = count

    return {
        "total_scans": total,
        "high_risk": counts["High"],
        "medium_risk": counts["Medium"],
        "low_risk": counts["Low"],
        "risk_distribution": [
            {"risk_level": level, "count": count}
            for level, count in counts.items()
        ],
    }
