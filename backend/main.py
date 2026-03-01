import hashlib
import os

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(title="BGConnect API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict:
    return {"data": {"status": "ok"}, "error": None}


@app.get("/health/nightscout")
async def nightscout_health() -> dict:
    url = os.getenv("NIGHTSCOUT_URL")
    secret = os.getenv("NIGHTSCOUT_API_SECRET")
    api_secret = hashlib.sha1(secret.encode()).hexdigest()

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{url}/api/v1/entries",
            headers={"api-secret": api_secret},
            params={"count": 1},
            timeout=10,
        )
        response.raise_for_status()
        try:
            entries = response.json()
        except Exception:
            return {
                "data": None,
                "error": f"Non-JSON response (status {response.status_code}): {response.text[:300]}",
            }

    return {
        "data": {
            "status": "ok",
            "latest_entry": entries[0] if entries else None,
        },
        "error": None,
    }
