"""
Unit tests for GarminConnector normalization logic.
Uses synthetic fixture data based on known Garmin API response shapes.
"""

import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from connectors.garmin import GarminConnector

USER_ID = "test_user"

# -------------------------------------------------------------------------
# Fixture data
# -------------------------------------------------------------------------

ACTIVITY = {
    "activityId": 12345678901,
    "activityName": "Morning Run",
    "startTimeGMT": "2026-02-28 12:30:00",
    "startTimeLocal": "2026-02-28 07:30:00",
    "activityType": {"typeKey": "running", "typeId": 1},
    "duration": 1734.0,
    "distance": 5432.1,
    "calories": 412,
    "averageHR": 158,
    "maxHR": 179,
    "steps": 6234,
}

ACTIVITY_NO_OPTIONALS = {
    "activityId": 99999,
    "activityName": "Strength Training",
    "startTimeGMT": "2026-02-28 18:00:00",
    "activityType": {"typeKey": "strength_training"},
    "duration": 3600.0,
}

HEART_RATE = {
    "restingHeartRate": 52,
    "maxHeartRate": 179,
    "heartRateValues": [
        [1772341200000, 72],
        [1772341320000, 68],
        [1772341440000, None],  # null value — should be skipped
    ],
}

HEART_RATE_NO_DATA = {"heartRateValues": []}

SLEEP = {
    "dailySleepDTO": {
        "sleepTimeSeconds": 27180,
        "sleepScores": {
            "overall": {"value": 78},
        },
    }
}

SLEEP_NO_DATA = {"dailySleepDTO": {"sleepTimeSeconds": 0}}

STRESS = {"avgStressLevel": 32}

STRESS_NO_DATA = {"avgStressLevel": -1}

TODAY = date(2026, 2, 28)


# -------------------------------------------------------------------------
# Activity
# -------------------------------------------------------------------------

class TestNormalizeActivity:
    def test_basic_fields(self):
        a = GarminConnector._normalize_activity(ACTIVITY, USER_ID)
        assert a.id == str(ACTIVITY["activityId"])
        assert a.user_id == USER_ID
        assert a.activity_type == "running"
        assert a.source == "garmin"

    def test_timestamps_are_utc(self):
        a = GarminConnector._normalize_activity(ACTIVITY, USER_ID)
        assert a.started_at.tzinfo == timezone.utc
        assert a.ended_at.tzinfo == timezone.utc

    def test_started_at_parsed_from_gmt(self):
        a = GarminConnector._normalize_activity(ACTIVITY, USER_ID)
        assert a.started_at == datetime(2026, 2, 28, 12, 30, 0, tzinfo=timezone.utc)

    def test_ended_at_derived_from_duration(self):
        a = GarminConnector._normalize_activity(ACTIVITY, USER_ID)
        expected_seconds = int(ACTIVITY["duration"])
        delta = (a.ended_at - a.started_at).seconds
        assert delta == expected_seconds

    def test_hr_fields(self):
        a = GarminConnector._normalize_activity(ACTIVITY, USER_ID)
        assert a.avg_hr == 158
        assert a.max_hr == 179

    def test_optional_fields_none_when_missing(self):
        a = GarminConnector._normalize_activity(ACTIVITY_NO_OPTIONALS, USER_ID)
        assert a.distance_meters is None
        assert a.calories is None
        assert a.avg_hr is None
        assert a.max_hr is None

    def test_name_in_metadata(self):
        a = GarminConnector._normalize_activity(ACTIVITY, USER_ID)
        assert a.metadata["name"] == "Morning Run"

    def test_steps_in_metadata(self):
        a = GarminConnector._normalize_activity(ACTIVITY, USER_ID)
        assert a.metadata["steps"] == 6234


# -------------------------------------------------------------------------
# Heart rate
# -------------------------------------------------------------------------

class TestNormalizeHeartRate:
    def test_returns_list_of_readings(self):
        readings = GarminConnector._normalize_heart_rate(HEART_RATE, USER_ID)
        assert isinstance(readings, list)

    def test_null_bpm_values_skipped(self):
        readings = GarminConnector._normalize_heart_rate(HEART_RATE, USER_ID)
        assert len(readings) == 2  # third sample has None bpm — skipped

    def test_basic_fields(self):
        reading = GarminConnector._normalize_heart_rate(HEART_RATE, USER_ID)[0]
        assert reading.id == "hr-1772341200000"
        assert reading.user_id == USER_ID
        assert reading.bpm == 72
        assert reading.source == "garmin"

    def test_timestamp_is_utc(self):
        from datetime import timezone
        reading = GarminConnector._normalize_heart_rate(HEART_RATE, USER_ID)[0]
        assert reading.timestamp.tzinfo == timezone.utc

    def test_empty_data_returns_empty_list(self):
        result = GarminConnector._normalize_heart_rate(HEART_RATE_NO_DATA, USER_ID)
        assert result == []


# -------------------------------------------------------------------------
# Sleep
# -------------------------------------------------------------------------

class TestNormalizeSleep:
    def test_basic_fields(self):
        s = GarminConnector._normalize_sleep(SLEEP, TODAY, USER_ID)
        assert s is not None
        assert s.id == f"sleep-{TODAY.isoformat()}"
        assert s.user_id == USER_ID
        assert s.duration_seconds == 27180
        assert s.score == 78
        assert s.source == "garmin"

    def test_date_stored_as_iso_string(self):
        s = GarminConnector._normalize_sleep(SLEEP, TODAY, USER_ID)
        assert s.date == "2026-02-28"

    def test_zero_sleep_returns_none(self):
        result = GarminConnector._normalize_sleep(SLEEP_NO_DATA, TODAY, USER_ID)
        assert result is None


# -------------------------------------------------------------------------
# Stress
# -------------------------------------------------------------------------

class TestNormalizeStress:
    def test_basic_fields(self):
        s = GarminConnector._normalize_stress(STRESS, TODAY, USER_ID)
        assert s is not None
        assert s.id == f"stress-{TODAY.isoformat()}"
        assert s.user_id == USER_ID
        assert s.avg_stress == 32
        assert s.source == "garmin"

    def test_date_stored_as_iso_string(self):
        s = GarminConnector._normalize_stress(STRESS, TODAY, USER_ID)
        assert s.date == "2026-02-28"

    def test_negative_stress_returns_none(self):
        result = GarminConnector._normalize_stress(STRESS_NO_DATA, TODAY, USER_ID)
        assert result is None
