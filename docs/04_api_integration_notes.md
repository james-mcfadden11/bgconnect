# API Integration Notes

*BGConnect | Version 1.3 | March 2026*

## Data Pipeline Architecture

```
Tandem Source  →  tconnectsync  →  Nightscout  →  BGConnect
Dexcom G7      →  Dexcom Share  →  Nightscout  →  BGConnect
Garmin Connect →  python-garminconnect          →  BGConnect (future)
```

---

## Nightscout (Priority 1 — Primary Data Source)

### Overview
Nightscout is an open source, self-hosted diabetes data platform with a REST API. BGConnect uses this API to fetch CGM readings, insulin doses, pump events, and site change records.

**Production instance:** https://nightscout.bgconnect.io

### Authentication
- Nightscout uses an `API_SECRET` token for authentication
- API calls include the header: `api-secret: <sha1(API_SECRET)>`
- The raw secret is stored in `backend/.env` and hashed by the connector on each request

### Key Endpoints

All endpoints require the `.json` suffix to return JSON. Without it, Nightscout returns tab-separated text.

| Endpoint | Method | Purpose |
|----------|--------|---------|
| GET /api/v1/entries.json | GET | CGM readings (SGV entries) |
| GET /api/v1/treatments.json | GET | Boluses, basals, site changes, notes |
| GET /api/v1/devicestatus.json | GET | Pump status, IOB, reservoir level |
| GET /api/v1/profile | GET | Insulin profile (basal rates, ratios, ISF) |
| POST /api/v1/treatments | POST | Create a treatment (used for annotations) |

### Query Parameters
- `count` — max records to return (set to 10000 for date range queries)
- `find[dateString][$gte]` / `find[dateString][$lte]` — date filter for entries
- `find[created_at][$gte]` / `find[created_at][$lte]` — date filter for treatments and devicestatus
- `find[eventType]` — filter treatments by type

### Treatment Event Types (as synced by tconnectsync)

| Event Type | Data | Notes |
|------------|------|-------|
| Combo Bolus | insulin, carbs | Tandem's bolus type — covers meal and correction boluses |
| Temp Basal | rate, absolute, duration | Control-IQ algorithm adjustments |
| Sleep | duration | Control-IQ sleep mode — no insulin fields |
| Site Change | — | Infusion site change; location not captured |

> **Note:** Tandem via tconnectsync does not use the standard Nightscout event types (Bolus, Meal Bolus, Correction Bolus). All bolus events arrive as `Combo Bolus`.

### Connector Interface

```python
async def fetch_glucose(user_id: str, start: datetime, end: datetime) -> List[GlucoseReading]
async def fetch_insulin(user_id: str, start: datetime, end: datetime) -> List[InsulinDose]
async def fetch_carbs(user_id: str, start: datetime, end: datetime) -> List[CarbEntry]
async def fetch_site_changes(user_id: str, start: datetime, end: datetime) -> List[SiteChange]
async def fetch_device_status(user_id: str, start: datetime, end: datetime) -> List[DeviceStatus]
```

### Known Limitations
- Device status returns empty — tconnectsync does not push pump status to Nightscout
- Site change location is not captured in Nightscout — must be annotated manually in BGConnect
- `dateString` in entries is local time; the connector uses the `date` millisecond timestamp instead for reliable UTC conversion

---

## tconnectsync (Pump Data Bridge)

### Overview
tconnectsync automatically syncs Tandem Source pump data to Nightscout by reverse-engineering Tandem's undocumented internal APIs. BGConnect does not interact with tconnectsync directly — it runs as a separate Docker container and populates Nightscout, which BGConnect reads from.

**Repo:** https://github.com/jwoglom/tconnectsync

### Data Synced to Nightscout
- Bolus data (as `Combo Bolus` events with insulin and carb amounts)
- Temp basal rate changes (Control-IQ algorithm adjustments)
- Control-IQ mode events (Sleep, Exercise)
- Site change events

### Risk Notes
- Uses Tandem's undocumented APIs — could break if Tandem changes their backend
- Has a track record of adapting: survived the t:connect to Tandem Source migration
- Monitor the tconnectsync GitHub for issues after Tandem firmware or app updates

---

## Dexcom Share (CGM Data Bridge)

### Overview
Nightscout has a built-in Dexcom Share bridge configured via environment variables. It polls the Dexcom Share API and pulls CGM readings automatically every 5 minutes. No separate tooling required.

---

## Garmin (Priority 2 — Future)

### Overview
Garmin activity, heart rate, sleep, and stress data via the `python-garminconnect` library. Deferred until after the dashboard MVP.

### Authentication Approach
- The official Garmin Health API requires enterprise developer access — not available to individuals
- `python-garminconnect` (cyberjunky) uses the same OAuth flow as the Garmin Connect mobile app, authenticating with email and password
- Tokens are cached in `~/.garth` after first login
- Credentials stored in `backend/.env` as `GARMIN_EMAIL` and `GARMIN_PASSWORD`
- Connectivity confirmed working via `garmin_test.py`

### Data Available
- Activities (type, duration, distance, heart rate)
- All-day heart rate
- Sleep (duration, score, stages)
- Stress levels

### Docker Consideration
- Token cache (`~/.garth`) must be accessible inside the backend container
- Mount `~/.garth` as a volume or handle first-time auth before container startup

---

## Other Potential Integrations

| Source | Priority | Notes |
|--------|----------|-------|
| Garmin (python-garminconnect) | Medium | Activity, HR, sleep, stress — after dashboard MVP |
| Apple Health | Low | Activity and HR on iOS |
| Tidepool | Low | Only viable if automatic Tandem sync is resolved |
| Manual CSV import | Low | Useful for historical data backfill |
