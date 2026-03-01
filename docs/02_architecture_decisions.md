# Architecture Decision Record (ADR)

*BGConnect | Version 1.3 | February 2026*

## ADR-001: Backend Framework — FastAPI (Python)

**Status: Accepted**

### Context
The backend needs to handle authentication and data fetching from third-party APIs, data transformation, and serve an analysis API to the frontend.

### Decision
Use FastAPI as the backend framework.

### Rationale
- Native async support suits the pattern of making external API calls
- Automatic OpenAPI/Swagger documentation aids development and onboarding
- Strong ecosystem for data analysis (pandas, numpy, scipy, statsmodels)
- OAuth2 utilities built in for future multi-user auth

---

## ADR-002: No Local Database in Phase 1

**Status: Accepted**

### Context
Adding a full database layer before core analysis features are validated adds significant complexity with little benefit at this stage.

### Decision
Phase 1 uses no local database for health data. Nightscout is the system of record. BGConnect fetches and normalizes data from Nightscout at request time. Annotations are stored in SQLite as they are user-generated data with no upstream source.

### Rationale
- Eliminates the ingest pipeline, deduplication logic, and schema migrations from the initial build
- Avoids storing PHI locally, reducing compliance exposure
- The normalization layer is identical whether data flows to a DB or directly to the API response

### Consequences
- Dashboard response times depend on Nightscout API latency
- No offline access to health data

### Future State
PostgreSQL will be introduced when local storage becomes a clear performance or functionality requirement. See `03_data_model.md` for the target schema.

---

## ADR-003: Frontend — React + TypeScript

**Status: Accepted**

### Decision
Use React with TypeScript for the frontend, with Recharts for time-series charting.

### Rationale
- TypeScript catches integration bugs at compile time
- Recharts is well-suited to time-series data visualization
- Aligns with existing JavaScript/TypeScript background

---

## ADR-004: Primary Data Backend — Nightscout

**Status: Accepted & Validated**

### Context
Tidepool was initially considered but its Tandem integration requires manual USB upload. Nightscout combined with tconnectsync provides a fully automatic pipeline for both pump and CGM data.

### Decision
Use Nightscout as the primary data backend. BGConnect reads from Nightscout's REST API.

### Validation
Nightscout is running in production at nightscout.bgconnect.io on a DigitalOcean Droplet. Both CGM and pump data are confirmed flowing automatically.

### Consequences
- Nightscout is a single-user system — multi-user requires each user to provide their own Nightscout URL and API secret
- No OAuth flow — authentication is simpler but requires users to manage their own Nightscout credentials

---

## ADR-005: Automatic Pump Data Pipeline — tconnectsync

**Status: Accepted & Validated**

### Decision
Use tconnectsync (github.com/jwoglom/tconnectsync) to automatically sync Tandem Source pump data to Nightscout. Runs as a Docker container with --auto-update flag, polling every 5 minutes.

### Validation
tconnectsync is running in production. On first run it synced 486 pump events and uploaded current insulin profiles. Polling every 5 minutes and confirmed writing to Nightscout.

### Risk
- Uses Tandem's undocumented internal APIs — could break if Tandem changes their backend
- Risk accepted — no official alternative exists for automatic sync
- tconnectsync has a track record of adapting to Tandem API changes

---

## ADR-006: Integration Plugin Architecture

**Status: Accepted**

### Decision
Define a standard connector interface that all data source integrations must implement. Nightscout is the first implementation.

### Rationale
- Prevents Nightscout-specific logic from leaking into the analysis or API layer
- New integrations require only a new connector module

---

## ADR-007: Containerization — Docker Compose

**Status: Accepted & Validated**

### Decision
Docker Compose for all services. Production stack on DigitalOcean Droplet: Nightscout, MongoDB, tconnectsync, Caddy. Development stack on local Mac: FastAPI, React dev server.

### Validation
Production Docker Compose stack is running on bgconnect.io DigitalOcean Droplet. All four containers healthy and restarting automatically on failure.

### Infrastructure Details
- Host: DigitalOcean Droplet, Ubuntu 24.04, $6/month
- Domain: bgconnect.io via Cloudflare
- SSL: Caddy with automatic Let's Encrypt certificate for nightscout.bgconnect.io
- DNS: nightscout.bgconnect.io and app.bgconnect.io both pointing at Droplet IP
- Docker version 29.2.1, Docker Compose v5.0.2
