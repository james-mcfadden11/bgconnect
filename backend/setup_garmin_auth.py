"""
One-time Garmin authentication setup.

Run this on your Mac (NOT inside Docker) before starting the stack for the first time,
or any time your Garmin session expires.

Usage:
    python3 backend/setup_garmin_auth.py

Tokens are saved to backend/.garth/ which is mounted into the Docker container
at /app/.garth — no further configuration needed.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from garminconnect import Garmin

load_dotenv("backend/.env")

email = os.getenv("GARMIN_EMAIL")
password = os.getenv("GARMIN_PASSWORD")

if not email or not password:
    sys.exit("Set GARMIN_EMAIL and GARMIN_PASSWORD in backend/.env")

tokenstore = str(Path("backend/.garth").resolve())
Path(tokenstore).mkdir(exist_ok=True)

print(f"Authenticating as {email}...")
print("If you have 2FA enabled, you will be prompted for a code.\n")

client = Garmin(email, password)
client.login()
client.garth.dump(tokenstore)

print(f"\nTokens saved to {tokenstore}")
print("You can now start the Docker stack with: docker compose up")
