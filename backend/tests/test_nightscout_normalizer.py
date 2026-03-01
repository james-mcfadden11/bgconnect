"""
Unit tests for NightscoutConnector normalization logic.
Uses fixture data captured from the live Nightscout instance.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from connectors.nightscout import NightscoutConnector

FIXTURES = Path(__file__).parent / "fixtures"

with open(FIXTURES / "entries.json") as f:
    ENTRIES = json.load(f)

with open(FIXTURES / "treatments.json") as f:
    TREATMENTS = json.load(f)

COMBO_BOLUSES = [t for t in TREATMENTS if t.get("eventType") == "Combo Bolus"]
TEMP_BASALS = [t for t in TREATMENTS if t.get("eventType") == "Temp Basal"]
SLEEP_EVENTS = [t for t in TREATMENTS if t.get("eventType") == "Sleep"]

USER_ID = "test_user"


# -----------------------------------------------------------------------------
# Glucose
# -----------------------------------------------------------------------------

class TestNormalizeGlucose:
    def test_basic_fields(self):
        entry = ENTRIES[0]
        reading = NightscoutConnector._normalize_glucose(entry, USER_ID)
        assert reading.id == str(entry["_id"])
        assert reading.user_id == USER_ID
        assert reading.value_mgdl == float(entry["sgv"])
        assert reading.source == "nightscout"

    def test_timestamp_is_utc(self):
        entry = ENTRIES[0]
        reading = NightscoutConnector._normalize_glucose(entry, USER_ID)
        assert reading.timestamp.tzinfo == timezone.utc
        # Verify against known millisecond timestamp
        expected = datetime.fromtimestamp(entry["date"] / 1000, tz=timezone.utc)
        assert reading.timestamp == expected

    def test_trend_direction(self):
        entry = ENTRIES[0]
        reading = NightscoutConnector._normalize_glucose(entry, USER_ID)
        assert reading.trend == entry.get("direction", "unknown")

    def test_missing_direction_defaults_to_unknown(self):
        entry = {**ENTRIES[0]}
        del entry["direction"]
        reading = NightscoutConnector._normalize_glucose(entry, USER_ID)
        assert reading.trend == "unknown"

    def test_all_fixtures_parse(self):
        readings = [NightscoutConnector._normalize_glucose(e, USER_ID) for e in ENTRIES]
        assert len(readings) == len(ENTRIES)
        assert all(r.value_mgdl > 0 for r in readings)


# -----------------------------------------------------------------------------
# Bolus (Combo Bolus)
# -----------------------------------------------------------------------------

class TestNormalizeBolus:
    def test_basic_fields(self):
        bolus = COMBO_BOLUSES[0]
        dose = NightscoutConnector._normalize_bolus(bolus, USER_ID)
        assert dose.id == str(bolus["_id"])
        assert dose.user_id == USER_ID
        assert dose.units == float(bolus["insulin"])
        assert dose.source == "nightscout"
        assert dose.duration_minutes is None

    def test_dose_type_is_bolus(self):
        dose = NightscoutConnector._normalize_bolus(COMBO_BOLUSES[0], USER_ID)
        assert dose.dose_type == "bolus"

    def test_timestamp_is_utc(self):
        dose = NightscoutConnector._normalize_bolus(COMBO_BOLUSES[0], USER_ID)
        assert dose.timestamp.tzinfo is not None

    def test_carbs_in_metadata(self):
        bolus = COMBO_BOLUSES[0]
        dose = NightscoutConnector._normalize_bolus(bolus, USER_ID)
        assert dose.metadata["carbs"] == bolus.get("carbs")

    def test_correction_bolus_dose_type(self):
        treatment = {**COMBO_BOLUSES[0], "eventType": "Correction Bolus"}
        dose = NightscoutConnector._normalize_bolus(treatment, USER_ID)
        assert dose.dose_type == "correction"

    def test_all_combo_boluses_parse(self):
        doses = [NightscoutConnector._normalize_bolus(t, USER_ID) for t in COMBO_BOLUSES]
        assert len(doses) == len(COMBO_BOLUSES)
        assert all(d.units > 0 for d in doses)


# -----------------------------------------------------------------------------
# Temp Basal
# -----------------------------------------------------------------------------

class TestNormalizeTempBasal:
    def test_basic_fields(self):
        tb = TEMP_BASALS[0]
        dose = NightscoutConnector._normalize_temp_basal(tb, USER_ID)
        assert dose is not None
        assert dose.id == str(tb["_id"])
        assert dose.dose_type == "temp_basal"
        assert dose.units == float(tb["absolute"])
        assert dose.source == "nightscout"

    def test_rate_in_metadata(self):
        dose = NightscoutConnector._normalize_temp_basal(TEMP_BASALS[0], USER_ID)
        assert dose.metadata["rate_u_per_hr"] == TEMP_BASALS[0]["absolute"]

    def test_zero_duration_stored_as_none(self):
        tb = {**TEMP_BASALS[0], "duration": 0}
        dose = NightscoutConnector._normalize_temp_basal(tb, USER_ID)
        assert dose.duration_minutes is None

    def test_nonzero_duration_preserved(self):
        tb = {**TEMP_BASALS[1], "duration": 5}
        dose = NightscoutConnector._normalize_temp_basal(tb, USER_ID)
        assert dose.duration_minutes == 5

    def test_missing_rate_returns_none(self):
        tb = {**TEMP_BASALS[0]}
        del tb["absolute"]
        del tb["rate"]
        result = NightscoutConnector._normalize_temp_basal(tb, USER_ID)
        assert result is None

    def test_all_temp_basals_parse(self):
        doses = [NightscoutConnector._normalize_temp_basal(t, USER_ID) for t in TEMP_BASALS]
        assert all(d is not None for d in doses)


# -----------------------------------------------------------------------------
# Carbs
# -----------------------------------------------------------------------------

class TestNormalizeCarb:
    def test_basic_fields(self):
        bolus = COMBO_BOLUSES[0]
        carb = NightscoutConnector._normalize_carb(bolus, USER_ID)
        assert carb.id == str(bolus["_id"])
        assert carb.user_id == USER_ID
        assert carb.carbs_grams == float(bolus["carbs"])
        assert carb.source == "nightscout"

    def test_timestamp_is_utc(self):
        carb = NightscoutConnector._normalize_carb(COMBO_BOLUSES[0], USER_ID)
        assert carb.timestamp.tzinfo is not None

    def test_notes_preserved(self):
        bolus = COMBO_BOLUSES[0]
        carb = NightscoutConnector._normalize_carb(bolus, USER_ID)
        assert carb.notes == bolus.get("notes")

    def test_all_carb_treatments_parse(self):
        carb_treatments = [t for t in COMBO_BOLUSES if t.get("carbs")]
        carbs = [NightscoutConnector._normalize_carb(t, USER_ID) for t in carb_treatments]
        assert all(c.carbs_grams > 0 for c in carbs)


# -----------------------------------------------------------------------------
# Sleep events — should not appear in insulin or carb results
# -----------------------------------------------------------------------------

class TestSleepEventsIgnored:
    def test_sleep_not_in_bolus_types(self):
        for event in SLEEP_EVENTS:
            assert event.get("eventType") not in NightscoutConnector.BOLUS_EVENT_TYPES

    def test_sleep_not_in_carb_types(self):
        for event in SLEEP_EVENTS:
            assert event.get("eventType") not in NightscoutConnector.CARB_EVENT_TYPES

    def test_sleep_not_in_temp_basal_types(self):
        for event in SLEEP_EVENTS:
            assert event.get("eventType") not in NightscoutConnector.TEMP_BASAL_EVENT_TYPES


# -----------------------------------------------------------------------------
# Site change (synthetic — no site changes in recent live data)
# -----------------------------------------------------------------------------

class TestNormalizeSiteChange:
    SITE_CHANGE = {
        "_id": "abc123",
        "eventType": "Site Change",
        "created_at": "2026-02-28T10:00:00.000Z",
        "notes": "left abdomen",
        "enteredBy": "Pump (tconnectsync)",
    }

    def test_basic_fields(self):
        sc = NightscoutConnector._normalize_site_change(self.SITE_CHANGE, USER_ID)
        assert sc.id == "abc123"
        assert sc.user_id == USER_ID
        assert sc.source == "nightscout"

    def test_location_is_none(self):
        # Location is annotated manually — Nightscout doesn't store it
        sc = NightscoutConnector._normalize_site_change(self.SITE_CHANGE, USER_ID)
        assert sc.location is None

    def test_notes_preserved(self):
        sc = NightscoutConnector._normalize_site_change(self.SITE_CHANGE, USER_ID)
        assert sc.notes == "left abdomen"

    def test_all_site_change_event_types_recognised(self):
        for etype in NightscoutConnector.SITE_CHANGE_EVENT_TYPES:
            treatment = {**self.SITE_CHANGE, "eventType": etype}
            sc = NightscoutConnector._normalize_site_change(treatment, USER_ID)
            assert sc.source == "nightscout"


# -----------------------------------------------------------------------------
# Device status (synthetic — tconnectsync doesn't push to Nightscout)
# -----------------------------------------------------------------------------

class TestNormalizeDeviceStatus:
    STATUS = {
        "_id": "def456",
        "created_at": "2026-02-28T10:00:00.000Z",
        "pump": {
            "reservoir": 180.5,
            "battery": {"percent": 85},
        },
        "iob": {"iob": 2.3},
    }

    def test_basic_fields(self):
        ds = NightscoutConnector._normalize_device_status(self.STATUS, USER_ID)
        assert ds.id == "def456"
        assert ds.user_id == USER_ID
        assert ds.source == "nightscout"

    def test_iob_parsed(self):
        ds = NightscoutConnector._normalize_device_status(self.STATUS, USER_ID)
        assert ds.iob == 2.3

    def test_reservoir_parsed(self):
        ds = NightscoutConnector._normalize_device_status(self.STATUS, USER_ID)
        assert ds.reservoir_units == 180.5

    def test_battery_parsed(self):
        ds = NightscoutConnector._normalize_device_status(self.STATUS, USER_ID)
        assert ds.battery_percent == 85

    def test_missing_optional_fields_are_none(self):
        status = {"_id": "xyz", "created_at": "2026-02-28T10:00:00.000Z"}
        ds = NightscoutConnector._normalize_device_status(status, USER_ID)
        assert ds.iob is None
        assert ds.reservoir_units is None
        assert ds.battery_percent is None
