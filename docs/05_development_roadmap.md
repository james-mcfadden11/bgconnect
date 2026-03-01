# Development Roadmap

*BGConnect | Version 1.4 | March 2026*

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

### Milestone 1.3 — Garmin Connector ← CURRENT

- [ ] Implement Garmin connector using python-garminconnect (cyberjunky library)
- [ ] Implement connector interface: fetch_activities, fetch_heart_rate, fetch_sleep, fetch_stress
- [ ] Map Garmin activity data to normalized activity schema
- [ ] Write unit tests for normalization logic using fixture data from live Garmin account
- [ ] Handle OAuth token storage for Docker environment (~/.garth)

### Milestone 1.4 — FastAPI Routes

- [ ] GET /glucose — normalized CGM readings for a date range
- [ ] GET /insulin — bolus, correction, and temp basal data for a date range
- [ ] GET /carbs — carb entries for a date range
- [ ] GET /site-changes — site change events
- [ ] GET /activities — Garmin activity data for a date range
- [ ] GET /annotations — manually logged annotations
- [ ] POST /annotations — create a new annotation (stored in SQLite)

### Milestone 1.5 — Dashboard MVP

- [ ] BG trend chart: time-series line chart for CGM readings
- [ ] Overlay insulin doses on the BG chart
- [ ] Overlay carb entries on the BG chart
- [ ] Activity overlay on BG trend chart (exercise events, heart rate)
- [ ] Date range picker
- [ ] Site change markers on the timeline
- [ ] Manual annotation entry form (category, value, notes, timestamp)

### Milestone 1.6 — Analysis Tools (v1)

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
