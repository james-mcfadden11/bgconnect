from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AnnotationCreate(BaseModel):
    timestamp: datetime
    category: str   # exercise, illness, stress, food, site_location, other
    value: str
    notes: Optional[str] = None


class Annotation(AnnotationCreate):
    id: str
    user_id: str
    created_at: datetime
