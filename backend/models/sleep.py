from typing import Optional
from pydantic import BaseModel


class SleepRecord(BaseModel):
    id: str
    user_id: str
    date: str           # ISO date string YYYY-MM-DD (the morning after the sleep)
    duration_seconds: int
    score: Optional[int]
    source: str
