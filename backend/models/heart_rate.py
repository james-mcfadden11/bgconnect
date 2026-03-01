from typing import Optional
from pydantic import BaseModel


class HeartRateDay(BaseModel):
    id: str
    user_id: str
    date: str        # ISO date string YYYY-MM-DD
    resting_hr: int
    max_hr: Optional[int]
    source: str
