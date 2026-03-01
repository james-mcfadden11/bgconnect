from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter

from connectors.nightscout import ConnectorError
from routes.deps import USER_ID, nightscout

router = APIRouter()


@router.get("/carbs")
async def get_carbs(
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> dict:
    s = start or datetime.now(timezone.utc) - timedelta(days=7)
    e = end or datetime.now(timezone.utc)
    try:
        data = await nightscout().fetch_carbs(USER_ID, s, e)
        return {"data": [r.model_dump(mode="json") for r in data], "error": None}
    except ConnectorError as exc:
        return {"data": None, "error": str(exc)}
