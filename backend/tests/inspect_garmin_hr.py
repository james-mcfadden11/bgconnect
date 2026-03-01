import sys
sys.path.insert(0, "/app")
import os
from dotenv import load_dotenv
load_dotenv()
from garminconnect import Garmin

c = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
c.login("/app/.garth")
data = c.get_heart_rates("2026-03-01")
vals = data.get("heartRateValues", [])
print("total samples:", len(vals))
print("first 3:", vals[:3])
print("last 3:", vals[-3:])
print("resting:", data.get("restingHeartRate"))
