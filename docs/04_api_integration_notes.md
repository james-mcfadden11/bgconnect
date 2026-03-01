# API Integration Notes

*BGConnect | Version 1.2 | February 2026*

## Data Pipeline Architecture

```
Tandem Source  →  tconnectsync  →  Nightscout  →  BGConnect
Dexcom G7      →  Dexcom Share  →  Nightscout  →  BGConnect
```

---

## Nightscout (Priority 1 — Primary Data Source)

### Overview
Nightscout is an open source, self-hosted diabetes data platform with a REST API. BGConnect uses this API to fetch CGM readings, insulin doses, pump events, and site change records.

**Production instance:** https://nightscout.bgconnect.io

### Authentication
- Nightscout uses an `API_SECRET` token for authentication
- API calls include the header: `api-secret: <sha1(API_SECRET)>`
- For multi-user phase 2, each user provides their own Nightscout URL and API secret

### Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| GET /api/v1/entries | GET | CGM readings (SGV entries) |
| GET /api/v1/treatments | GET | Boluses, basals, site changes, notes |
| GET /api/v1/profile | GET | Insulin profile (basal rates, ratios, ISF) |
| POST /api/v1/treatments | POST | Create a treatment (used for annotations) |
| GET /api/v1/devicestatus | GET | Pump status, IOB, reservoir level |

### Query Parameters
- `count` — number of records to return
- `find[dateString][$gte]` — start date filter
- `find[dateString][$lte]` — end date filter
- `find[eventType]` — filter treatments by type (e.g. Site Change, Bolus)

### Data Types Available via Nightscout
- **SGV** — CGM readings from Dexcom G7 via Dexcom Share
- **Bolus** — bolus doses from t:slim via tconnectsync
- **Temp Basal** — temporary basal rate changes
- **Site Change** — infusion set change events (note: location not captured, must be annotated manually)
- **Cannula Fill, Cartridge Change** — pump maintenance events
- **Profile** — basal rates, carb ratios, insulin sensitivity factors

### Important Notes
- Site Change events confirm a change occurred but do not capture location — location must be logged as an annotation in BGConnect
- All timestamps should be normalized to UTC on ingest
- Nightscout's `dateString` is local-time — handle timezone carefully
- Implement exponential backoff — Nightscout instances may be self-hosted on modest hardware

### Connector Interface

All future connectors must implement the same interface:

```python
def fetch_glucose(user_id: str, start: datetime, end: datetime) -> List[GlucoseReading]
def fetch_insulin(user_id: str, start: datetime, end: datetime) -> List[InsulinDose]
def fetch_site_changes(user_id: str, start: datetime, end: datetime) -> List[SiteChange]
def fetch_device_status(user_id: str, start: datetime, end: datetime) -> List[DeviceStatus]
```

---

## tconnectsync (Pump Data Bridge)

### Overview
tconnectsync automatically syncs Tandem Source pump data to Nightscout by reverse-engineering Tandem's undocumented internal APIs. BGConnect does not interact with tconnectsync directly — it runs as a separate Docker container and populates Nightscout, which BGConnect reads from.

**Repo:** https://github.com/jwoglom/tconnectsync

### Data Synced to Nightscout
- Basal data (scheduled, temp, and Control-IQ algorithm adjustments)
- Bolus data (manual and correction boluses)
- Pump events (cartridge change, cannula fill, alarms, sleep/exercise mode)
- Insulin profiles (basal rates, carb ratios, correction factors)

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
Garmin activity, heart rate, sleep, and stress data via the Garmin Health API. Deferred until the Nightscout integration is stable and validated.

### Key Notes
- Requires applying to Garmin's developer program for API access
- Uses OAuth 1.0a for authentication
- Garmin Health API is webhook-based — Garmin pushes data to your endpoint on sync
- This means a publicly accessible server endpoint is required (already have this)
- Activity data maps to the `activity_sessions` normalized schema
- No changes to BGConnect's core needed — add a new connector module only

---

## Other Potential Integrations

| Source | Priority | Notes |
|--------|----------|-------|
| Garmin Health API | Medium | Activity, HR, sleep, stress — phase 2 |
| Apple Health | Low | Activity and HR on iOS |
| Tidepool | Low | Only viable if automatic Tandem sync is resolved |
| Manual CSV import | Low | Useful for historical data backfill |
