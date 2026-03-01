import hashlib
import os
from contextlib import asynccontextmanager

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.database import init_db
from routes.glucose import router as glucose_router
from routes.insulin import router as insulin_router
from routes.carbs import router as carbs_router
from routes.site_changes import router as site_changes_router
from routes.activities import router as activities_router
from routes.annotations import router as annotations_router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="BGConnect API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(glucose_router, prefix="/api")
app.include_router(insulin_router, prefix="/api")
app.include_router(carbs_router, prefix="/api")
app.include_router(site_changes_router, prefix="/api")
app.include_router(activities_router, prefix="/api")
app.include_router(annotations_router, prefix="/api")


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
            f"{url}/api/v1/entries.json",
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
