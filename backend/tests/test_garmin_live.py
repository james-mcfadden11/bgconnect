"""
End-to-end connectivity test for GarminConnector.
Fetches real data from the live Garmin Connect account.

Run with:
    docker compose exec backend python tests/test_garmin_live.py
"""

import asyncio
import sys
from datetime import datetime, timezone

sys.path.insert(0, "/app")

from connectors.garmin import GarminConnector


async def main() -> None:
    c = GarminConnector()
    start = datetime(2026, 2, 25, 0, 0, 0, tzinfo=timezone.utc)
    end = datetime(2026, 3, 1, 23, 59, 59, tzinfo=timezone.utc)

    activities = await c.fetch_activities("test", start, end)
    heart_rate = await c.fetch_heart_rate("test", start, end)
    sleep = await c.fetch_sleep("test", start, end)
    stress = await c.fetch_stress("test", start, end)

    print(f"activities:  {len(activities)}")
    if activities:
        a = activities[0]
        print(f"             latest: {a.activity_type} — {a.duration_seconds // 60} min @ {a.started_at}")

    print(f"heart_rate:  {len(heart_rate)} days")
    if heart_rate:
        print(f"             latest: resting {heart_rate[0].resting_hr} bpm on {heart_rate[0].date}")

    print(f"sleep:       {len(sleep)} nights")
    if sleep:
        s = sleep[0]
        print(f"             latest: {s.duration_seconds // 3600}h {(s.duration_seconds % 3600) // 60}m, score {s.score} on {s.date}")

    print(f"stress:      {len(stress)} days")
    if stress:
        print(f"             latest: avg {stress[0].avg_stress} on {stress[0].date}")


asyncio.run(main())
