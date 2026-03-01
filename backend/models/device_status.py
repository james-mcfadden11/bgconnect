from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class DeviceStatus(BaseModel):
    id: str
    user_id: str
    timestamp: datetime  # UTC
    iob: Optional[float]  # insulin on board (units)
    reservoir_units: Optional[float]
    battery_percent: Optional[int]
    source: str
