
from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DatabaseSession
from app.models.scan import Scan
from app.schemas.scan import ScanRequest
from app.services.detection_service import analyze_url

router = APIRouter(prefix="/scans", tags=["URL Scanner"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def scan_url(
    data: ScanRequest,
    db: DatabaseSession,
    current_user: CurrentUser,
):
    try:
        result = analyze_url(data.url)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    scan = Scan(
        user_id=current_user.id,
        url=result["url"],
        risk_level=result["risk_level"],
        risk_score=result["risk_score"],
        explanation=result["explanation"],
    )

    db.add(scan)
    db.commit()
    db.refresh(scan)

    return {
        "id": scan.id,
        "url": scan.url,
        "risk_score": scan.risk_score,
        "risk_level": scan.risk_level,
        "verdict": result["verdict"],
        "explanation": scan.explanation,
        "harm_explanation": result["harm_explanation"],
        "findings": result["findings"],
        "features": result["features"],
        "created_at": scan.created_at,

        "detection_method": result["detection_method"],
        "ml_label": result["ml_label"],
        "ml_prediction": result["ml_prediction"],
        "ml_phishing_probability": result["ml_phishing_probability"],
        "ml_decision_score": result["ml_decision_score"],
        "ml_error": result["ml_error"],

        "heuristic_score": result["heuristic_score"],
        "score_type": result["score_type"],
        "threat_intelligence": result["threat_intelligence"]
    }