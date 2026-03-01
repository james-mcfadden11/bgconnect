from datetime import datetime
from pydantic import BaseModel


class HeartRateReading(BaseModel):
    id: str
    user_id: str
    timestamp: datetime  # UTC
    bpm: int
    source: str
