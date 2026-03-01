"""
End-to-end connectivity test for NightscoutConnector.
Fetches real data from the live Nightscout instance.

Run with:
    docker compose exec backend python tests/test_connector_live.py
"""

import asyncio
import sys
from datetime import datetime, timezone

sys.path.insert(0, "/app")

from connectors.nightscout import NightscoutConnector


async def main() -> None:
    c = NightscoutConnector()
    start = datetime(2026, 2, 28, 0, 0, 0, tzinfo=timezone.utc)
    end = datetime(2026, 3, 1, 23, 59, 59, tzinfo=timezone.utc)

    glucose = await c.fetch_glucose("test", start, end)
    insulin = await c.fetch_insulin("test", start, end)
    carbs = await c.fetch_carbs("test", start, end)
    site_changes = await c.fetch_site_changes("test", start, end)
    device_status = await c.fetch_device_status("test", start, end)

    print(f"glucose:       {len(glucose)} readings")
    if glucose:
        print(f"               latest: {glucose[0].value_mgdl} mg/dL @ {glucose[0].timestamp}")

    print(f"insulin:       {len(insulin)} doses")
    if insulin:
        print(f"               types: {sorted({d.dose_type for d in insulin})}")

    print(f"carbs:         {len(carbs)} entries")
    if carbs:
        print(f"               latest: {carbs[0].carbs_grams}g @ {carbs[0].timestamp}")

    print(f"site_changes:  {len(site_changes)}")
    print(f"device_status: {len(device_status)}")


asyncio.run(main())
