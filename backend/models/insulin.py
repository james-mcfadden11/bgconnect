from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class InsulinDose(BaseModel):
    id: str
    user_id: str
    timestamp: datetime  # UTC
    dose_type: str  # bolus, correction, temp_basal
    units: float  # delivered units for bolus/correction; U/hr rate for temp_basal
    duration_minutes: Optional[int]  # set for temp_basal
    source: str
    metadata: dict
