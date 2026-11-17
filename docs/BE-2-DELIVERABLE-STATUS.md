# BE-2 implementation package - review status

This package is a repository-aligned implementation proposal for issue [#7](https://github.com/HUNT3Rboii/SWAFY-/issues/7). It does not replace or modify the frozen BE-1 contract.

## Acceptance mapping

| BE-2 criterion | Package contents | Review status |
|---|---|---|
| FastAPI + `/health` | `apps/api/src/swafy_api/main.py`, `api/routes/health.py` | Implemented |
| Alembic + PostGIS | `alembic.ini`, `migrations/env.py`, model metadata, GiST index | Framework and metadata implemented; initial revision reserved for Atallah |
| Dockerfile | `apps/api/Dockerfile` | Implemented |
| Users with roles | `models/user.py`, `models/enums.py` | Implemented |
| Reports and required fields/photo keys | `models/report.py` | Implemented |
| Status history and confirmations | `models/report.py` | Implemented |
| GiST index on location | `Report.__table_args__` | Implemented in metadata; materialized by initial migration |
| Register/login/refresh JWT | `api/routes/auth.py`, `services/auth.py`, `core/security.py` | Implemented |
| Citizen/admin role enforcement support | `api/dependencies.py`; registration is always citizen; admin bootstrap command | Implemented |
| Separate worker service token | `api/dependencies.py` | Implemented; ready for BE-4 internal routes |
| Automated tests and CI | `tests/`, `.github/workflows/ci-apps-api.yml` | Added; requires PostGIS service |

## Submission gate

**Do not close BE-2 yet.** The initial Alembic revision is intentionally absent because the issue states that only Atallah writes migrations. Once Atallah authors/reviews and commits the initial revision, apply it to PostGIS, run the API test suite, and verify the GiST index in PostgreSQL. The database-backed authentication routes are not usable until that migration is applied.

The tests create their schema from SQLAlchemy metadata in a dedicated database whose name must contain `test`; the fixture refuses to run against the regular development database. This verifies the model mapping and endpoint behavior, but it is not a substitute for validating the owner-authored Alembic revision.

## Architecture decisions

- Passwords are stored as Argon2id hashes, never as plaintext.
- Access tokens and refresh tokens are distinct JWT types. Refresh tokens are rotated and their `jti` values are recorded in `refresh_tokens` so replay and logout revocation are enforced.
- Public registration always creates `citizen`; municipal administrators are provisioned through the controlled bootstrap command, not public input.
- The worker authenticates using its own high-entropy bearer secret, checked with a constant-time comparison. It does not use a citizen JWT or receive database credentials.
- Report locations are WGS84 geometry points; the coordinate order is longitude, latitude.
- Photo object keys are internal fields and must never be serialized to public API responses.
- The implementation uses synchronous SQLAlchemy with psycopg 3, consistent with the modular-monolith scope and current Compose setup.

## Explicitly outside BE-2

Report creation/list/map, MinIO presigned uploads, the internal photo-check queue/result endpoints, status transition endpoints, export, nearby reports and confirmations HTTP endpoints remain later backend issues (BE-3/BE-4/BE-5). The models are prepared for them but those routes are not falsely marked as implemented here.
