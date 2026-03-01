# BGConnect — Project Overview & Vision

*Version 1.2 | February 2026*

## Problem Statement

People living with Type 1 diabetes using continuous glucose monitors (CGM) and insulin pumps generate rich streams of health data every day. However, the platforms that collect this data — Tandem Source, Dexcom Clarity, and others — are designed for clinical reporting, not for personal, hypothesis-driven analysis.

Key questions that are currently difficult or impossible to answer using existing tools:

- Does my infusion site location affect insulin absorption and BG levels?
- How does exercise type, timing, and intensity affect my insulin sensitivity?
- Are there patterns in my overnight BG that correlate with prior-day activity?
- Which controllable variables have the biggest impact on my time-in-range?

## Vision

BGConnect is a personal diabetes data analysis platform that aggregates CGM, pump, and activity data and provides an analysis layer for exploring how controllable variables affect glucose outcomes.

The platform is designed first as a personal tool, with an architecture that allows it to expand to support multiple users without a significant rewrite.

## Data Pipeline Overview

Data flows into Nightscout from two automatic sources, then BGConnect reads from Nightscout:

```
Tandem Source  →  tconnectsync  →  Nightscout  →  BGConnect
Dexcom G7      →  Dexcom Share  →  Nightscout  →  BGConnect
```

This architecture is fully automatic — no manual uploads required.

## Goals

### Primary Goals

- Fetch CGM and pump data from Nightscout on demand and present it in an analyzable form
- Provide a web dashboard for visualizing BG trends alongside pump and annotation data
- Enable controlled variable analysis — e.g. segment data by infusion site location, activity level, time of day
- Allow manual annotation of variables that no platform captures automatically (e.g. infusion site location)

### Secondary Goals

- Support additional data integrations (Garmin activity data, others) via a pluggable integration layer
- Add local data storage and caching as usage patterns become clear
- Provide a multi-user mode where each user connects their own Nightscout instance
- Remain open source so the community can extend it

## Non-Goals (v1)

- Local storage of raw health data (deferred — Nightscout is the system of record in phase 1)
- Real-time CGM monitoring or alerting (Nightscout already handles this)
- Clinical decision support or treatment recommendations
- Native mobile application

## Data Storage Philosophy

Phase 1 treats Nightscout as the system of record. BGConnect fetches data from the Nightscout API at request time, transforms it, and returns it to the dashboard. No raw health data is persisted locally by BGConnect.

Annotations (e.g. infusion site location, manual notes) are the one exception — these are user-generated data that no existing platform captures, so they are stored in a lightweight local store (SQLite) in phase 1.

## Target Users

### Phase 1 — Personal
A single user running the platform locally, with their own Nightscout instance populated by tconnectsync and Dexcom Share.

### Phase 2 — Shared Tool
Other users who run their own Nightscout instances and want to use BGConnect's analysis layer. Each user provides their own Nightscout URL and API secret. BGConnect does not store their raw health data.

### Phase 3 — Stored Data (Optional)
If performance or offline access becomes a requirement, a local PostgreSQL layer is added. Compliance considerations must be addressed before accepting third-party users' data.

## Success Criteria

- Can answer the question: does infusion site location affect my BG outcomes?
- Dashboard loads in under 5 seconds for 90 days of data via Nightscout API
- Pump and CGM data flows into Nightscout automatically with no manual intervention
- A second user can connect their own Nightscout instance without developer intervention
- Adding a new data source requires only a new connector module
