# BE-2 database migration handoff (for Atallah)

**Purpose:** implement the initial Alembic revision for BE-2 without creating a migration outside the repository's stated ownership rule.

The BE-2 issue explicitly says: **Only Atallah writes migrations.** The API package provides the SQLAlchemy model metadata and Alembic environment. This note is the review checklist for the migration owner.

## Source of truth

Models are in `apps/api/src/swafy_api/models/` and import into `Base.metadata` through `swafy_api.models`. Shared domain enum values must remain aligned with `docs/contracts/enums.md` and the frozen `docs/contracts/openapi.yaml`.

## Tables to create

| Table | Required fields / constraints |
|---|---|
| `users` | UUID PK; `display_name`; unique normalized `email`; `password_hash`; role (`citizen`, `municipal_admin`); active flag; timestamps |
| `reports` | UUID PK; owner FK; description; category; suggested category; status; photo_state; label_source; AI confidence/reason/provider; WGS84 POINT; quarantine/public/thumbnail object keys; content type/size; timestamps |
| `status_history` | UUID PK; report FK; nullable from_status; to_status; nullable changed_by user FK; changed_at; note |
| `confirmations` | UUID PK; report FK; user FK; created_at; unique `(report_id, user_id)` |
| `refresh_tokens` | `jti` UUID PK; user FK; expiry; revoked_at; created_at. Required for one-time refresh-token rotation and logout revocation. Store no raw JWT. |

## PostGIS and indexes

1. Execute `CREATE EXTENSION IF NOT EXISTS postgis` before creating the `reports.location` geometry column.
2. Create `reports.location` as `geometry(POINT, 4326)`; the API's coordinate convention is longitude then latitude.
3. Create `ix_reports_location_gist` using `USING GIST (location)`.
4. Preserve the model's owner/date, photo-state/status, status-history, confirmation, refresh-token and unique-email indexes/constraints.
5. Ensure the `report_status` enum is created once and reused by both `reports` and `status_history`; do not create duplicate PostgreSQL enum types.

## Enum values (frozen)

- `user_role`: `citizen`, `municipal_admin`
- `report_category`: `pothole`, `trash`, `graffiti`, `broken_light`, `other`
- `report_status`: `submitted`, `verified`, `in_progress`, `resolved`
- `photo_state`: `pending_check`, `approved`, `rejected`
- `label_source`: `manual`, `ai`, `ai_corrected`

The optional `suggested_category` column reuses the same PostgreSQL `report_category` enum type. Do not create a second enum type for suggested categories.

## Migration verification checklist

- [ ] `alembic upgrade head` succeeds against `postgis/postgis:16-3.4`.
- [ ] `alembic downgrade -1` and re-upgrade work on a disposable database.
- [ ] `SELECT postgis_version()` succeeds.
- [ ] `\d reports` shows `location geometry(Point,4326)`.
- [ ] `SELECT indexdef FROM pg_indexes WHERE indexname='ix_reports_location_gist'` shows a GiST index.
- [ ] All table names, FK delete actions, unique constraints and enum values match model metadata.
- [ ] The API auth tests pass after migration is applied.

## Generate and review

From `apps/api` with `PYTHONPATH=src` and `DATABASE_URL` configured:

```bash
alembic revision --autogenerate -m "initial BE-2 schema"
# Review/fix the generated extension and enum operations before applying.
alembic upgrade head
alembic current
alembic check
```

Alembic autogenerate may not produce the PostGIS extension operation. Add it explicitly at the beginning of `upgrade()` and remove it only if a shared database policy manages extensions separately.
