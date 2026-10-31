
from datetime import datetime

from pydantic import BaseModel, Field


class ScanRequest(BaseModel):
    url: str = Field(min_length=1, max_length=2048)


class ScanResponse(BaseModel):
    id: int
    url: str
    risk_score: float
    risk_level: str
    explanation: str
    findings: list[str]
    created_at: datetime
    detection_method: str = "heuristic"


class ScanHistoryItem(BaseModel):
    id: int
    url: str
    risk_score: float
    risk_level: str
    explanation: str
    created_at: datetime
