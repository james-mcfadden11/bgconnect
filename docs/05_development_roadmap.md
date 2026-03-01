# Development Roadmap

*BGConnect | Version 1.3 | February 2026*

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

### Milestone 1.1 — Project Setup ← CURRENT

- [ ] Apply for Garmin Health API developer access (approval can take time — do this first)
- [ ] Initialize Git repository and push to GitHub
- [ ] Define local Docker Compose stack: FastAPI + React dev server
- [ ] Set up Python virtual environment and dependency management
- [ ] Set up React + TypeScript frontend scaffolding
- [ ] Configure environment variable management (.env + python-dotenv)
- [ ] Verify local stack connects to Nightscout API at nightscout.bgconnect.io

### Milestone 1.2 — Nightscout Connector

- [ ] Implement Nightscout API client (auth, base request handling, error/retry logic)
- [ ] Implement connector interface: fetch_glucose, fetch_insulin, fetch_site_changes, fetch_device_status
- [ ] Implement normalization layer (Nightscout format -> internal schema)
- [ ] Write unit tests for normalization logic using fixture data from live Nightscout instance

### Milestone 1.3 — Garmin Connector

- [ ] Implement Garmin API client (OAuth, base request handling, error/retry logic)
- [ ] Implement connector interface: fetch_activities, fetch_heart_rate, fetch_sleep, fetch_stress
- [ ] Map Garmin activity data to normalized activity schema
- [ ] Write unit tests for normalization logic using fixture data from live Garmin account

### Milestone 1.4 — FastAPI Routes

- [ ] GET /glucose — normalized CGM readings for a date range
- [ ] GET /insulin — bolus and basal data for a date range
- [ ] GET /site-changes — site change events
- [ ] GET /activities — Garmin activity data for a date range
- [ ] GET /annotations — manually logged annotations
- [ ] POST /annotations — create a new annotation (stored in SQLite)

### Milestone 1.5 — Dashboard MVP

- [ ] BG trend chart: time-series line chart for CGM readings
- [ ] Overlay insulin doses on the BG chart
- [ ] Activity overlay on the BG trend chart (exercise events, heart rate)
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
| Activity data | Garmin Health API |
