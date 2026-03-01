import hashlib
import os
from datetime import datetime, timezone
from typing import Optional

import httpx
from dotenv import load_dotenv

from models.carbs import CarbEntry
from models.device_status import DeviceStatus
from models.glucose import GlucoseReading
from models.insulin import InsulinDose
from models.site_change import SiteChange

load_dotenv()


class ConnectorError(Exception):
    pass


class NightscoutConnector:
    # Tandem via tconnectsync uses "Combo Bolus" for all bolus types (meal + correction)
    BOLUS_EVENT_TYPES = {"Bolus", "Meal Bolus", "Correction Bolus", "Combo Bolus", "SMB", "Carb Correction"}
    CARB_EVENT_TYPES = {"Meal Bolus", "Carbs Only", "Combo Bolus"}
    TEMP_BASAL_EVENT_TYPES = {"Temp Basal"}
    SITE_CHANGE_EVENT_TYPES = {"Site Change", "Pump Site Change", "Reservoir Change", "Infusion Site Change"}

    def __init__(self) -> None:
        url = os.getenv("NIGHTSCOUT_URL")
        secret = os.getenv("NIGHTSCOUT_API_SECRET")
        if not url or not secret:
            raise ConnectorError("NIGHTSCOUT_URL and NIGHTSCOUT_API_SECRET must be set")
        self.base_url = url.rstrip("/")
        self.api_secret = hashlib.sha1(secret.encode()).hexdigest()

    async def _get(self, path: str, params: dict) -> list:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1{path}",
                    headers={"api-secret": self.api_secret},
                    params=params,
                    timeout=30,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            raise ConnectorError(
                f"Nightscout HTTP error {e.response.status_code}: {e.response.text[:200]}"
            )
        except httpx.RequestError as e:
            raise ConnectorError(f"Nightscout request failed: {e}")

    def _date_params(self, field: str, start: datetime, end: datetime) -> dict:
        return {
            f"find[{field}][$gte]": start.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            f"find[{field}][$lte]": end.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "count": 10000,
        }

    # -------------------------------------------------------------------------
    # Public fetch methods
    # -------------------------------------------------------------------------

    async def fetch_glucose(self, user_id: str, start: datetime, end: datetime) -> list[GlucoseReading]:
        params = self._date_params("dateString", start, end)
        params["find[type]"] = "sgv"
        data = await self._get("/entries.json", params)
        return [self._normalize_glucose(e, user_id) for e in data]

    async def fetch_insulin(self, user_id: str, start: datetime, end: datetime) -> list[InsulinDose]:
        data = await self._get("/treatments.json", self._date_params("created_at", start, end))
        doses = []
        for t in data:
            event_type = t.get("eventType", "")
            if event_type in self.BOLUS_EVENT_TYPES and t.get("insulin"):
                doses.append(self._normalize_bolus(t, user_id))
            elif event_type in self.TEMP_BASAL_EVENT_TYPES:
                dose = self._normalize_temp_basal(t, user_id)
                if dose is not None:
                    doses.append(dose)
        return doses

    async def fetch_carbs(self, user_id: str, start: datetime, end: datetime) -> list[CarbEntry]:
        data = await self._get("/treatments.json", self._date_params("created_at", start, end))
        return [
            self._normalize_carb(t, user_id)
            for t in data
            if t.get("eventType", "") in self.CARB_EVENT_TYPES and t.get("carbs")
        ]

    async def fetch_site_changes(self, user_id: str, start: datetime, end: datetime) -> list[SiteChange]:
        data = await self._get("/treatments.json", self._date_params("created_at", start, end))
        return [
            self._normalize_site_change(t, user_id)
            for t in data
            if t.get("eventType", "") in self.SITE_CHANGE_EVENT_TYPES
        ]

    async def fetch_device_status(self, user_id: str, start: datetime, end: datetime) -> list[DeviceStatus]:
        data = await self._get("/devicestatus.json", self._date_params("created_at", start, end))
        return [self._normalize_device_status(d, user_id) for d in data]

    # -------------------------------------------------------------------------
    # Normalization (static — testable without API access)
    # -------------------------------------------------------------------------

    @staticmethod
    def _normalize_glucose(entry: dict, user_id: str) -> GlucoseReading:
        # Use millisecond Unix timestamp for reliable UTC conversion
        timestamp = datetime.fromtimestamp(entry["date"] / 1000, tz=timezone.utc)
        return GlucoseReading(
            id=str(entry["_id"]),
            user_id=user_id,
            timestamp=timestamp,
            value_mgdl=float(entry["sgv"]),
            trend=entry.get("direction", "unknown"),
            source="nightscout",
        )

    @staticmethod
    def _normalize_bolus(treatment: dict, user_id: str) -> InsulinDose:
        timestamp = datetime.fromisoformat(treatment["created_at"].replace("Z", "+00:00"))
        event_type = treatment.get("eventType", "Bolus")
        dose_type = "correction" if "Correction" in event_type else "bolus"
        return InsulinDose(
            id=str(treatment["_id"]),
            user_id=user_id,
            timestamp=timestamp,
            dose_type=dose_type,
            units=float(treatment["insulin"]),
            duration_minutes=None,
            source="nightscout",
            metadata={
                "event_type": event_type,
                "carbs": treatment.get("carbs"),
            },
        )

    @staticmethod
    def _normalize_temp_basal(treatment: dict, user_id: str) -> Optional[InsulinDose]:
        # Prefer absolute rate; fall back to rate field
        rate = treatment.get("absolute") or treatment.get("rate")
        if rate is None:
            return None
        rate = float(rate)
        duration_minutes = int(treatment.get("duration", 0)) or None
        timestamp = datetime.fromisoformat(treatment["created_at"].replace("Z", "+00:00"))
        return InsulinDose(
            id=str(treatment["_id"]),
            user_id=user_id,
            timestamp=timestamp,
            dose_type="temp_basal",
            units=rate,  # U/hr — see duration_minutes for delivery window
            duration_minutes=duration_minutes,
            source="nightscout",
            metadata={
                "event_type": "Temp Basal",
                "rate_u_per_hr": rate,
                "percent": treatment.get("percent"),
            },
        )

    @staticmethod
    def _normalize_carb(treatment: dict, user_id: str) -> CarbEntry:
        timestamp = datetime.fromisoformat(treatment["created_at"].replace("Z", "+00:00"))
        return CarbEntry(
            id=str(treatment["_id"]),
            user_id=user_id,
            timestamp=timestamp,
            carbs_grams=float(treatment["carbs"]),
            source="nightscout",
            notes=treatment.get("notes"),
        )

    @staticmethod
    def _normalize_site_change(treatment: dict, user_id: str) -> SiteChange:
        timestamp = datetime.fromisoformat(treatment["created_at"].replace("Z", "+00:00"))
        return SiteChange(
            id=str(treatment["_id"]),
            user_id=user_id,
            timestamp=timestamp,
            location=None,  # annotated manually — not in Nightscout
            source="nightscout",
            notes=treatment.get("notes"),
        )

    @staticmethod
    def _normalize_device_status(status: dict, user_id: str) -> DeviceStatus:
        timestamp = datetime.fromisoformat(status["created_at"].replace("Z", "+00:00"))
        pump = status.get("pump", {})
        reservoir = pump.get("reservoir")
        battery = pump.get("battery", {}).get("percent") if isinstance(pump.get("battery"), dict) else None
        iob_data = status.get("iob", {})
        iob = iob_data.get("iob") if isinstance(iob_data, dict) else None
        return DeviceStatus(
            id=str(status["_id"]),
            user_id=user_id,
            timestamp=timestamp,
            iob=float(iob) if iob is not None else None,
            reservoir_units=float(reservoir) if reservoir is not None else None,
            battery_percent=int(battery) if battery is not None else None,
            source="nightscout",
        )
