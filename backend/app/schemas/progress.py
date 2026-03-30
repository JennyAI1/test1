from datetime import datetime

from pydantic import BaseModel


class ProgressEventCreate(BaseModel):
    app_key: str
    activity_type: str
    minutes_spent: float = 0
    metadata: dict = {}


class ProgressEventResponse(BaseModel):
    id: int
    app_key: str
    activity_type: str
    minutes_spent: float
    metadata: dict
    created_at: datetime


class ProgressSummary(BaseModel):
    total_minutes: float
    by_app: dict[str, float]
