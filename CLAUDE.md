# BGConnect

A personal diabetes data analysis platform that combines CGM, pump, and activity data into a unified dashboard with controlled variable analysis tools.

## What This App Does

- Fetches CGM and pump data from a live Nightscout instance at `nightscout.bgconnect.io`
- Provides a web dashboard for visualizing BG trends with insulin, site change, and annotation overlays
- Allows manual annotation of variables Nightscout doesn't capture (e.g. infusion site location)
- Enables correlation and segmentation analysis — e.g. "does site location affect BG outcomes?"

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python / FastAPI |
| Frontend | React + TypeScript + Recharts |
| Annotation storage | SQLite (phase 1) |
| Data backend | Nightscout REST API |
| Infrastructure | Docker Compose |
| Domain | bgconnect.io (Cloudflare DNS, DigitalOcean Droplet) |

## Project Structure

```
/
├── CLAUDE.md
├── docker-compose.yml        # local dev stack
├── docs/                     # full project documentation
├── backend/
│   ├── main.py               # FastAPI entry point
│   ├── connectors/           # data source connectors
│   │   └── nightscout.py     # Nightscout connector (primary)
│   ├── routes/               # API route handlers
│   ├── models/               # Pydantic data models
│   ├── db/                   # SQLite annotation storage
│   └── tests/
└── frontend/
    ├── src/
    │   ├── components/       # React components
    │   ├── pages/            # page-level components
    │   └── api/              # API client
    └── public/
```

## Environment Variables

Backend reads from `.env` in the `backend/` directory:

```
NIGHTSCOUT_URL=https://nightscout.bgconnect.io
NIGHTSCOUT_API_SECRET=<secret>
```

Never commit `.env` files.

## Nightscout API

Base URL: `https://nightscout.bgconnect.io/api/v1`

Authentication: header `api-secret: <sha1 hash of secret>`

Key endpoints:
- `GET /entries` — CGM readings (SGV). Params: `count`, `find[dateString][$gte]`, `find[dateString][$lte]`
- `GET /treatments` — bolus, basal, site changes, pump events. Params: `find[eventType]`, date filters
- `GET /profile` — insulin profiles (basal rates, carb ratios, ISF)
- `GET /devicestatus` — pump status, IOB, reservoir
- `POST /treatments` — create a treatment (used for annotations)

All timestamps are UTC. Nightscout's `dateString` field is local time — handle timezone carefully.

## Connector Interface

All data source connectors must implement:

```python
def fetch_glucose(user_id: str, start: datetime, end: datetime) -> List[GlucoseReading]
def fetch_insulin(user_id: str, start: datetime, end: datetime) -> List[InsulinDose]
def fetch_site_changes(user_id: str, start: datetime, end: datetime) -> List[SiteChange]
def fetch_device_status(user_id: str, start: datetime, end: datetime) -> List[DeviceStatus]
```

## Data Models (Normalized)

```python
class GlucoseReading:
    id: str
    user_id: str
    timestamp: datetime  # UTC
    value_mgdl: float
    trend: str           # flat, rising, falling, etc.
    source: str          # nightscout

class InsulinDose:
    id: str
    user_id: str
    timestamp: datetime
    dose_type: str       # bolus, basal, correction
    units: float
    duration_minutes: Optional[int]
    source: str
    metadata: dict

class SiteChange:
    id: str
    user_id: str
    timestamp: datetime
    location: Optional[str]  # annotated manually — not in Nightscout
    source: str
    notes: Optional[str]

class Annotation:
    id: str
    user_id: str
    timestamp: datetime
    category: str        # exercise, illness, stress, food, site_location, other
    value: str
    notes: Optional[str]
```

## Development Conventions

- Python: type hints on all functions, Pydantic models for all API request/response shapes
- All datetimes stored and returned as UTC ISO 8601 strings
- API routes return consistent envelope: `{ data: ..., error: null }`
- Connector errors should raise `ConnectorError` with a descriptive message
- Tests live alongside source in `tests/` — use pytest with fixture data from Nightscout responses
- Frontend: functional components only, no class components
- No hardcoded credentials anywhere — always use environment variables

## Key Decisions & Context

See `docs/` for full documentation:
- `02_architecture_decisions.md` — why we made key technology choices
- `04_api_integration_notes.md` — Nightscout API details and connector interface
- `03_data_model.md` — full schema including future PostgreSQL target
- `05_development_roadmap.md` — current milestone and what's been completed

## Current Status

Infrastructure is complete and running:
- Nightscout at `nightscout.bgconnect.io` with live CGM and pump data
- tconnectsync syncing Tandem Source → Nightscout every 5 minutes
- Dexcom Share bridge syncing G7 CGM data automatically

Currently at: **Milestone 1.1 — Project Setup**
