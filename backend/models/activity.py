from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ActivitySession(BaseModel):
    id: str
    user_id: str
    started_at: datetime  # UTC
    ended_at: datetime    # UTC
    activity_type: str    # running, cycling, walking, etc.
    duration_seconds: int
    distance_meters: Optional[float]
    calories: Optional[int]
    avg_hr: Optional[int]
    max_hr: Optional[int]
    source: str
    metadata: dict
