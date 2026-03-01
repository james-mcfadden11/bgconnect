from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SiteChange(BaseModel):
    id: str
    user_id: str
    timestamp: datetime  # UTC
    location: Optional[str]  # manually annotated — not in Nightscout
    source: str
    notes: Optional[str]
