import asyncio
import os
from datetime import datetime, timedelta, timezone, date as date_type
from typing import Optional

from dotenv import load_dotenv
from garminconnect import Garmin

from models.activity import ActivitySession
from models.heart_rate import HeartRateReading
from models.sleep import SleepRecord
from models.stress import StressDay

load_dotenv()

TOKENSTORE = os.path.join(os.path.dirname(__file__), "..", ".garth")


class ConnectorError(Exception):
    pass


class GarminConnector:
    def __init__(self) -> None:
        email = os.getenv("GARMIN_EMAIL")
        password = os.getenv("GARMIN_PASSWORD")
        if not email or not password:
            raise ConnectorError("GARMIN_EMAIL and GARMIN_PASSWORD must be set")
        self._email = email
        self._password = password
        self._client: Optional[Garmin] = None

    def _get_client(self) -> Garmin:
        if self._client is None:
            client = Garmin(self._email, self._password)
            client.login(TOKENSTORE)
            self._client = client
        return self._client

    # -------------------------------------------------------------------------
    # Public fetch methods
    # -------------------------------------------------------------------------

    async def fetch_activities(
        self, user_id: str, start: datetime, end: datetime
    ) -> list[ActivitySession]:
        client = self._get_client()
        data = await asyncio.to_thread(
            client.get_activities_by_date,
            start.strftime("%Y-%m-%d"),
            end.strftime("%Y-%m-%d"),
        )
        return [self._normalize_activity(a, user_id) for a in data]

    async def fetch_heart_rate(
        self, user_id: str, start: datetime, end: datetime
    ) -> list[HeartRateReading]:
        client = self._get_client()
        results = []
        for d in _date_range(start.date(), end.date()):
            data = await asyncio.to_thread(client.get_heart_rates, d.isoformat())
            results.extend(self._normalize_heart_rate(data, user_id))
        return [r for r in results if start <= r.timestamp <= end]

    async def fetch_sleep(
        self, user_id: str, start: datetime, end: datetime
    ) -> list[SleepRecord]:
        client = self._get_client()
        results = []
        for d in _date_range(start.date(), end.date()):
            data = await asyncio.to_thread(client.get_sleep_data, d.isoformat())
            record = self._normalize_sleep(data, d, user_id)
            if record is not None:
                results.append(record)
        return results

    async def fetch_stress(
        self, user_id: str, start: datetime, end: datetime
    ) -> list[StressDay]:
        client = self._get_client()
        results = []
        for d in _date_range(start.date(), end.date()):
            data = await asyncio.to_thread(client.get_stress_data, d.isoformat())
            record = self._normalize_stress(data, d, user_id)
            if record is not None:
                results.append(record)
        return results

    # -------------------------------------------------------------------------
    # Normalization (static — testable without API access)
    # -------------------------------------------------------------------------

    @staticmethod
    def _normalize_activity(activity: dict, user_id: str) -> ActivitySession:
        start_gmt = activity.get("startTimeGMT", "")
        started_at = datetime.strptime(start_gmt, "%Y-%m-%d %H:%M:%S").replace(
            tzinfo=timezone.utc
        )
        duration = int(activity.get("duration") or 0)
        ended_at = started_at + timedelta(seconds=duration)
        return ActivitySession(
            id=str(activity["activityId"]),
            user_id=user_id,
            started_at=started_at,
            ended_at=ended_at,
            activity_type=activity.get("activityType", {}).get("typeKey", "unknown"),
            duration_seconds=duration,
            distance_meters=activity.get("distance"),
            calories=activity.get("calories"),
            avg_hr=activity.get("averageHR"),
            max_hr=activity.get("maxHR"),
            source="garmin",
            metadata={
                "name": activity.get("activityName"),
                "steps": activity.get("steps"),
            },
        )

    @staticmethod
    def _normalize_heart_rate(data: dict, user_id: str) -> list[HeartRateReading]:
        readings = []
        for item in data.get("heartRateValues") or []:
            if not item or len(item) < 2 or item[1] is None:
                continue
            timestamp_ms, bpm = item[0], item[1]
            timestamp = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
            readings.append(HeartRateReading(
                id=f"hr-{timestamp_ms}",
                user_id=user_id,
                timestamp=timestamp,
                bpm=int(bpm),
                source="garmin",
            ))
        return readings

    @staticmethod
    def _normalize_sleep(
        data: dict, d: date_type, user_id: str
    ) -> Optional[SleepRecord]:
        daily = data.get("dailySleepDTO") or {}
        sleep_seconds = daily.get("sleepTimeSeconds") or 0
        if not sleep_seconds:
            return None
        score_obj = (daily.get("sleepScores") or {}).get("overall") or {}
        score = score_obj.get("value")
        return SleepRecord(
            id=f"sleep-{d.isoformat()}",
            user_id=user_id,
            date=d.isoformat(),
            duration_seconds=int(sleep_seconds),
            score=int(score) if score is not None else None,
            source="garmin",
        )

    @staticmethod
    def _normalize_stress(
        data: dict, d: date_type, user_id: str
    ) -> Optional[StressDay]:
        avg = data.get("avgStressLevel")
        if avg is None or int(avg) < 0:  # Garmin returns -1 when no data
            return None
        return StressDay(
            id=f"stress-{d.isoformat()}",
            user_id=user_id,
            date=d.isoformat(),
            avg_stress=int(avg),
            source="garmin",
        )


def _date_range(start: date_type, end: date_type) -> list[date_type]:
    dates = []
    current = start
    while current <= end:
        dates.append(current)
        current += timedelta(days=1)
    return dates
