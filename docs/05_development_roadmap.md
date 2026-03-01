# Development Roadmap

*BGConnect | Version 1.5 | March 2026*

## ✓ Pre-Development: Infrastructure Setup — COMPLETE

*Completed February 22, 2026*

- ✓ Registered bgconnect.io on Cloudflare
- ✓ Provisioned DigitalOcean Droplet (Ubuntu 24.04, $6/month, NYC region)
- ✓ Configured DNS: nightscout.bgconnect.io and app.bgconnect.io pointing at Droplet
- ✓ Installed Docker 29.2.1 and Docker Compose v5.0.2 on Droplet
- ✓ Deployed Nightscout via Docker Compose with MongoDB
- ✓ Configured Dexcom Share bridge — CGM data confirmed flowing
- ✓ Deployed tconnectsync — pump data confirmed flowing (486 events synced on first run, polling every 5 minutes)
- ✓ Deployed Caddy reverse proxy with automatic SSL certificate for nightscout.bgconnect.io
- ✓ Verified Nightscout accessible at https://nightscout.bgconnect.io with live CGM and pump data

---

## Phase 1 — Personal Tool (Local, No DB)

Goal: A working local stack that fetches data from Nightscout on demand and provides a web dashboard for exploration and analysis.

### ✓ Milestone 1.1 — Project Setup — COMPLETE

*Completed March 1, 2026*

- ✓ Confirmed Garmin data access via python-garminconnect (official Garmin Health API is enterprise-only)
- ✓ Initialized Git repository and pushed to GitHub (james-mcfadden11/bgconnect)
- ✓ Defined local Docker Compose stack: FastAPI backend + Vite/React dev server
- ✓ Set up Python dependency management via requirements.txt in Docker
- ✓ Set up React + TypeScript frontend scaffolding with Vite
- ✓ Configured environment variable management (backend/.env + python-dotenv)
- ✓ Verified local stack connects to Nightscout API at nightscout.bgconnect.io

### ✓ Milestone 1.2 — Nightscout Connector — COMPLETE

*Completed March 1, 2026*

- ✓ Implemented Nightscout API client (auth, base request handling, error handling)
- ✓ Implemented connector interface: fetch_glucose, fetch_insulin, fetch_carbs, fetch_site_changes, fetch_device_status
- ✓ Implemented normalization layer (Nightscout format -> internal schema)
- ✓ Added CarbEntry model and fetch_carbs — carb data synced from Tandem via tconnectsync
- ✓ Handles Tandem-specific event types: Combo Bolus, Temp Basal, Sleep (Control-IQ)
- ✓ 33 unit tests against live fixture data — all passing
- ✓ End-to-end verified: 496 glucose readings, 523 insulin doses, 15 carb entries over 2-day window

### ✓ Milestone 1.3 — Garmin Connector — COMPLETE

*Completed March 1, 2026*

- ✓ Implemented Garmin connector using python-garminconnect (cyberjunky library)
- ✓ Implemented connector interface: fetch_activities, fetch_heart_rate, fetch_sleep, fetch_stress
- ✓ Mapped Garmin activity data to normalized activity schema
- ✓ Intraday heart rate: ~349 samples/day, every ~2 min, parsed from [[timestamp_ms, bpm], ...] format
- ✓ Written unit tests for all normalization logic (activity, heart rate, sleep, stress)
- ✓ OAuth token storage handled via ~/.garth, mounted into Docker via volume

### ✓ Milestone 1.4 — FastAPI Routes — COMPLETE

*Completed March 1, 2026*

- ✓ GET /api/glucose — normalized CGM readings for a date range
- ✓ GET /api/insulin — bolus, correction, and temp basal data for a date range
- ✓ GET /api/carbs — carb entries for a date range
- ✓ GET /api/site-changes — site change events
- ✓ GET /api/activities — Garmin activity data for a date range
- ✓ GET /api/heart-rate — intraday Garmin heart rate samples for a date range
- ✓ GET /api/annotations — manually logged annotations
- ✓ POST /api/annotations — create a new annotation (stored in SQLite)

### ✓ Milestone 1.5 — Dashboard MVP — COMPLETE

*Completed March 1, 2026*

- ✓ Combined time-series chart: BG, heart rate, and insulin boluses overlaid on a shared x-axis
- ✓ Dual Y-axis: mg/dL (left) and bpm (right)
- ✓ Reference lines at 70 mg/dL (low) and 180 mg/dL (high)
- ✓ Date selector with previous/next day navigation — supports viewing any historical day
- ✓ Chart x-axis fixed to the selected calendar day (local midnight to midnight)
- ✓ Stats summary: BG reading count, bolus count, HR sample count

Deferred to Milestone 1.6:
- [ ] Carb entry overlay on BG chart
- [ ] Site change markers on the timeline
- [ ] Manual annotation entry form (category, value, notes, timestamp)

### Milestone 1.6 — Dashboard Continued + Analysis Tools (v1)

- [ ] Carb entry overlay on BG chart
- [ ] Site change markers on the timeline
- [ ] Manual annotation entry form (category, value, notes, timestamp)
- [ ] Time-in-range summary (by day, week, month)
- [ ] Segment BG data by site location — compare mean BG and TIR across locations
- [ ] Basic correlation view: select two variables (including Garmin activity variables), see scatter plot
- [ ] Export data to CSV

---

## Phase 2 — Shared Tool (Hosted)

Goal: Deploy the app so other users can connect their own Nightscout instances.

### Milestone 2.1 — Multi-User Support

- [ ] Add user accounts with JWT-based session management
- [ ] Each user stores their Nightscout URL and API secret (encrypted at rest)
- [ ] All API routes and annotation storage scoped to authenticated user
- [ ] User registration and login UI

### Milestone 2.2 — Cloud Deployment

- [ ] Deploy app to bgconnect.io Droplet alongside Nightscout
- [ ] Configure app.bgconnect.io routing in Caddyfile
- [ ] Set up CI/CD pipeline (GitHub Actions)
- [ ] Configure production environment secrets

---

## Phase 3 — Local Data Storage (Optional)

Introduce PostgreSQL if performance or offline access becomes a genuine requirement.

- [ ] Add PostgreSQL to Docker Compose
- [ ] Implement SQLAlchemy models and Alembic migrations per the data model document
- [ ] Add ingest pipeline: connector fetches from Nightscout, writes to DB
- [ ] Switch API routes to query DB instead of calling Nightscout directly
- [ ] Compliance review before accepting third-party user data

---

## [DRAFT] Analysis North Star — Personalized ISF Modeling

*This is a working concept, not yet scoped into milestones. Captured here to inform architecture decisions as the project evolves.*

The goal is a personalized, continuously updating model of insulin sensitivity (ISF) as a function of real-world variables.

Rather than looking for clean isolated events, we model every 5-minute CGM interval across the full time series. The pharmacokinetic relationships between insulin, carbs, and BG are used as the structural foundation — IOB curves, COB curves, basal activity — and ISF is treated as a parameter that varies based on contextual factors like recent activity, exercise intensity, sleep quality, time of day, and days into an infusion site.

### Pipeline

**Layer 1 — Data Assembly**
Joins CGM, pump, and Garmin data into a unified time series with consistent timestamps and no gaps.

**Layer 2 — Feature Engineering**
Computes derived variables: IOB at each timestep, COB curves, trailing activity load windows, sleep debt, site age, sensor age.

**Layer 3 — Modeling**
Fits a Bayesian or mixed-effects model where ISF is a latent variable estimated from observed BG response after accounting for all known factors. Uncertainty is explicit — the model knows what it doesn't know, and confidence tightens as data accumulates.

**Layer 4 — Output**
Surfaces actionable insights: how ISF varies by time of day, activity load, sleep quality, site location. Not just charts but concrete, personalized relationships you can act on.

### Implications for the Roadmap

Everything in Phase 1 — the Nightscout connector, Garmin integration, data model, dashboard — is infrastructure that feeds this layer. Key prerequisites before modeling work begins:

- Reliable, gap-free time series for CGM, insulin (including temp basal), and carbs
- Garmin intraday HR and activity data aligned to CGM timestamps
- Site change and annotation data to enable site-age and contextual features
- Local data storage (Phase 3) to support offline feature engineering at scale

---

## Tech Stack Summary

| Layer | Technology |
|-------|-----------|
| Backend | Python / FastAPI |
| Annotation storage (phase 1) | SQLite |
| Health data storage (phase 3) | PostgreSQL + SQLAlchemy + Alembic |
| Frontend | React + TypeScript + Recharts |
| Infrastructure | Docker Compose — DigitalOcean Droplet (bgconnect.io) |
| Domain & DNS | bgconnect.io via Cloudflare |
| SSL & Routing | Caddy (automatic Let's Encrypt) |
| CI/CD | GitHub Actions (phase 2) |
| Primary data backend | Nightscout REST API (nightscout.bgconnect.io) |
| Pump data bridge | tconnectsync (Tandem Source -> Nightscout) |
| CGM data bridge | Dexcom Share -> Nightscout bridge |
| Activity data | python-garminconnect (unofficial OAuth wrapper) |
