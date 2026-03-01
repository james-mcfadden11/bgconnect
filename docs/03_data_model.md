# Data Model & Schema Design

*BGConnect | Version 1.0 | February 2026*

> This document describes the target database schema for Phase 3 when PostgreSQL is introduced. In Phase 1, health data is not stored locally — Nightscout is the system of record. Only annotations are stored locally (SQLite).

## Design Principles

- Every table has a `user_id` column — multi-tenancy is built in from the start
- All timestamps stored in UTC
- `source` and `source_id` columns track provenance of every record
- A `metadata` JSONB column on key tables allows flexible annotation without schema migrations
- Normalized glucose readings stored in a single table regardless of source

## Core Tables

### users

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | Primary key |
| nightscout_url | VARCHAR | User's Nightscout instance URL |
| created_at | TIMESTAMPTZ | Account creation time |
| metadata | JSONB | Flexible user-level settings |

### glucose_readings

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | Primary key |
| user_id | UUID FK | References users.id |
| timestamp | TIMESTAMPTZ | Time of reading (UTC) |
| value_mgdl | NUMERIC | BG in mg/dL |
| trend | VARCHAR | flat, rising, falling, etc. |
| source | VARCHAR | nightscout, manual |
| source_id | VARCHAR | ID from source system (dedup key) |

### insulin_doses

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | Primary key |
| user_id | UUID FK | References users.id |
| timestamp | TIMESTAMPTZ | Dose delivery time (UTC) |
| dose_type | VARCHAR | bolus, correction, temp_basal |
| units | NUMERIC | Delivered units for bolus/correction; U/hr rate for temp_basal |
| duration_minutes | INTEGER | Set for temp_basal; null for bolus |
| source | VARCHAR | nightscout, manual |
| source_id | VARCHAR | Dedup key |
| metadata | JSONB | event_type, carbs (if meal bolus), rate_u_per_hr (if temp_basal) |

### carb_entries

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | Primary key |
| user_id | UUID FK | References users.id |
| timestamp | TIMESTAMPTZ | Time of carb entry (UTC) |
| carbs_grams | NUMERIC | Grams of carbohydrate |
| source | VARCHAR | nightscout, manual |
| source_id | VARCHAR | Dedup key |
| notes | TEXT | Optional free text |

> Carb entries are synced from the Tandem pump via tconnectsync as `Combo Bolus` treatments. A single Combo Bolus produces both an `InsulinDose` and a `CarbEntry`.

### site_changes

Key table for the infusion site location research question.

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | Primary key |
| user_id | UUID FK | References users.id |
| timestamp | TIMESTAMPTZ | Time of site change (UTC) |
| location | VARCHAR | abdomen-L, abdomen-R, flank-L, etc. |
| days_at_site | INTEGER | Computed: days since prior change |
| source | VARCHAR | nightscout, manual |
| notes | TEXT | Free text — bleeding, scar tissue, etc. |
| metadata | JSONB | Cannula type, insertion angle, etc. |

### annotations

General-purpose table for manually logged variables — exercise notes, illness, stress, food quality, or any future variable not captured by another table.

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | Primary key |
| user_id | UUID FK | References users.id |
| timestamp | TIMESTAMPTZ | Event time (UTC) |
| category | VARCHAR | exercise, illness, stress, food, site_location, other |
| value | VARCHAR | Freeform or controlled vocab value |
| notes | TEXT | Optional free text |
| metadata | JSONB | Source-specific structured data |

### activity_sessions

Populated by the Garmin integration (phase 2) or manually.

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | Primary key |
| user_id | UUID FK | References users.id |
| started_at | TIMESTAMPTZ | Activity start (UTC) |
| ended_at | TIMESTAMPTZ | Activity end (UTC) |
| activity_type | VARCHAR | walking, running, cycling, etc. |
| intensity | VARCHAR | low, moderate, high, or HR zone |
| source | VARCHAR | garmin, manual, apple_health |
| source_id | VARCHAR | Dedup key |
| metadata | JSONB | HR avg/max, steps, calories, etc. |

## Indexes

- glucose_readings: (user_id, timestamp)
- insulin_doses: (user_id, timestamp)
- site_changes: (user_id, timestamp)
- annotations: (user_id, timestamp, category)
- activity_sessions: (user_id, started_at)

## Deduplication Strategy

Records from Nightscout carry a source_id from Nightscout's internal IDs. On upsert, (user_id, source, source_id) is used as the uniqueness key. This allows the sync pipeline to run repeatedly without creating duplicate records.
