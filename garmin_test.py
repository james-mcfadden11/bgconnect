"""
Quick connectivity test for Garmin Connect.
Authenticates and pulls recent activity and health data.

Usage:
    Create a .env file with:
        GARMIN_EMAIL=your@email.com
        GARMIN_PASSWORD=yourpassword

    Then run:
        python3 garmin_test.py
"""

import os
from datetime import date, timedelta
from dotenv import load_dotenv
from garminconnect import Garmin

load_dotenv()

email = os.getenv("GARMIN_EMAIL")
password = os.getenv("GARMIN_PASSWORD")

if not email or not password:
    raise SystemExit("Set GARMIN_EMAIL and GARMIN_PASSWORD in a .env file")

print(f"Authenticating as {email}...")
client = Garmin(email, password)
client.login()
print("Login successful.\n")

today = date.today()
yesterday = today - timedelta(days=1)

# Heart rate
print("--- Heart Rate (yesterday) ---")
hr = client.get_heart_rates(yesterday.isoformat())
print(f"  Resting HR: {hr.get('restingHeartRate')} bpm")
print(f"  Max HR: {hr.get('maxHeartRate')} bpm")

# Steps
print("\n--- Steps (yesterday) ---")
steps = client.get_steps_data(yesterday.isoformat())
print(f"  Records returned: {len(steps)}")
if steps:
    total = sum(s.get("steps", 0) for s in steps)
    print(f"  Total steps: {total}")

# Sleep
print("\n--- Sleep (last night) ---")
sleep = client.get_sleep_data(today.isoformat())
daily = sleep.get("dailySleepDTO", {})
print(f"  Sleep score: {daily.get('sleepScores', {}).get('overall', {}).get('value', 'N/A')}")
print(f"  Duration: {daily.get('sleepTimeSeconds', 0) // 3600}h {(daily.get('sleepTimeSeconds', 0) % 3600) // 60}m")

# Stress
print("\n--- Stress (yesterday) ---")
stress = client.get_stress_data(yesterday.isoformat())
print(f"  Average stress: {stress.get('avgStressLevel', 'N/A')}")

# Activities (last 5)
print("\n--- Recent Activities ---")
activities = client.get_activities(0, 5)
for a in activities:
    print(f"  {a.get('startTimeLocal', 'N/A')[:10]}  {a.get('activityType', {}).get('typeKey', 'N/A'):<20}  {a.get('distance', 0)/1000:.1f} km  {int(a.get('duration', 0) // 60)} min")

print("\nAll checks passed. Garmin connectivity confirmed.")
