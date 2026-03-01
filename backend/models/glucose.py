from datetime import datetime
from pydantic import BaseModel


class GlucoseReading(BaseModel):
    id: str
    user_id: str
    timestamp: datetime  # UTC
    value_mgdl: float
    trend: str  # flat, rising, falling, etc.
    source: str
