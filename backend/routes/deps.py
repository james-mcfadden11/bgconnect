"""
Lazy connector singletons — one instance per connector, reused across requests.
"""

from connectors.garmin import GarminConnector
from connectors.nightscout import NightscoutConnector

_nightscout: NightscoutConnector | None = None
_garmin: GarminConnector | None = None

USER_ID = "default"


def nightscout() -> NightscoutConnector:
    global _nightscout
    if _nightscout is None:
        _nightscout = NightscoutConnector()
    return _nightscout


def garmin() -> GarminConnector:
    global _garmin
    if _garmin is None:
        _garmin = GarminConnector()
    return _garmin
