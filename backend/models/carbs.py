from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CarbEntry(BaseModel):
    id: str
    user_id: str
    timestamp: datetime  # UTC
    carbs_grams: float
    source: str
    notes: Optional[str]
