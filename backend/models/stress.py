from pydantic import BaseModel


class StressDay(BaseModel):
    id: str
    user_id: str
    date: str       # ISO date string YYYY-MM-DD
    avg_stress: int
    source: str
