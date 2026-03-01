from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter

from db.annotations import create_annotation, list_annotations
from models.annotation import AnnotationCreate
from routes.deps import USER_ID

router = APIRouter()


@router.get("/annotations")
async def get_annotations(
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> dict:
    s = start or datetime.now(timezone.utc) - timedelta(days=30)
    e = end or datetime.now(timezone.utc)
    data = await list_annotations(USER_ID, s, e)
    return {"data": [r.model_dump(mode="json") for r in data], "error": None}


@router.post("/annotations")
async def post_annotation(body: AnnotationCreate) -> dict:
    annotation = await create_annotation(body, USER_ID)
    return {"data": annotation.model_dump(mode="json"), "error": None}
