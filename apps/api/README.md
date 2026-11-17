# SWAFY API (BE-2)

FastAPI backend scaffold for the SWAFY v1 contract. The public contract remains `../../docs/contracts/openapi.yaml`; do not create a second contract or change generated client types in this issue.

## Included in this BE-2 package

- FastAPI application mounted at `/api/v1`, with `/api/v1/health` and a hidden `/health` compatibility probe for the existing Caddy/deploy smoke test.
- SQLAlchemy 2 models for users, reports, status history, confirmations, and refresh-token revocation.
- WGS84 PostGIS `POINT` for report location and an explicit PostgreSQL GiST index.
- Register, login, refresh-token rotation, and idempotent logout routes matching the BE-1 contract's response envelope.
- Citizen/admin role enum, role dependency for later admin routes, and a dedicated constant-time-checked worker service-token dependency.
- Alembic environment, Dockerfile, tests, and admin bootstrap command.

## Run the stack

From the repository root:

```powershell
cd infra
Copy-Item .env.example .env
Copy-Item env/api.env.example env/api.env
# Edit infra/env/api.env: set DATABASE_URL, JWT_SECRET and WORKER_SERVICE_TOKEN.
docker compose up -d db minio minio-init
docker compose --profile api up --build api
```

The API listens on port `8000`; the versioned base URL is `http://localhost:8000/api/v1`. Check:

```powershell
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/health
```

Both health probes return `{"status":"ok"}`. The API intentionally does not run migrations or create tables at startup.

## Database migrations - owner action required

The BE-2 issue says **only Atallah writes migrations**. Alembic is configured and all models are registered, but this package intentionally does not include an initial revision written by another contributor. See [`migrations/README.md`](migrations/README.md) and [`../../docs/BE-2-MIGRATION-HANDOFF.md`](../../docs/BE-2-MIGRATION-HANDOFF.md).

After Atallah commits the initial PostGIS-aware revision, apply it from this directory:

```powershell
$env:DATABASE_URL = "postgresql+psycopg://swafy:swafy-dev-password@localhost:5432/swafy"
alembic upgrade head
alembic current
```

Until that revision is applied, `/health` works but database-backed auth endpoints cannot be considered ready.

## Authentication contract

| Endpoint | Access token | Result |
|---|---|---|
| `POST /auth/register` | Public | Creates a citizen; returns user and token pair (201) |
| `POST /auth/login` | Public | Verifies password; returns user and token pair (200) |
| `POST /auth/refresh` | Refresh JWT in body | Revokes the old refresh token and returns a rotated pair (200) |
| `POST /auth/logout` | Access JWT + refresh JWT in body | Revokes that user's refresh token; returns 204 |

All routes are under `/api/v1`. Access JWTs last 15 minutes by default; refresh JWTs last 14 days by default. A refresh token is one-time-use and its `jti` is stored server-side. Only a hashed password is stored. Public registration always creates `citizen`; the request cannot supply a role.

### Create the first municipal administrator

Do not expose admin registration publicly. Run the bootstrap command from the API container or a shell with the API environment loaded:

```powershell
$env:ADMIN_EMAIL = "admin@example.com"
$env:ADMIN_DISPLAY_NAME = "Municipal Administrator"
$env:ADMIN_PASSWORD = "use-a-unique-password-of-at-least-12-chars"
python -m swafy_api.scripts.create_admin
```

The command refuses to overwrite an existing account.

## Worker service authentication

BE-2 provides `require_worker_service` for BE-4's internal worker routes. It checks `Authorization: Bearer <WORKER_SERVICE_TOKEN>` with a constant-time comparison. This credential is not a citizen/admin JWT and is never issued by `/auth/*`. Do not give the worker database credentials.

## Environment variables

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | PostgreSQL/PostGIS connection URL |
| `JWT_SECRET` | Signing key for user access/refresh JWTs |
| `JWT_ALGORITHM` | Currently `HS256` |
| `JWT_ISSUER`, `JWT_AUDIENCE` | Token validation context |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime; 15 by default |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime; 14 by default |
| `WORKER_SERVICE_TOKEN` | Separate internal worker bearer credential |
| `CORS_ORIGINS` | Comma-separated browser origins |
| `ENVIRONMENT` | `development`, `test`, or `production` |

Production refuses placeholder or short signing/service secrets. Set `ENVIRONMENT=production` in `infra/env/api.prod.env`; the current infra example does not set this variable yet. Generate independent random secrets (at least 32 characters); never reuse the JWT secret as the worker token. Ask the infra owner to add `ENVIRONMENT=production` to the production API env example and `ENVIRONMENT=development` to the development API env example. Do not commit `.env` files.

## Tests

The test suite requires PostgreSQL with PostGIS. It uses a dedicated `swafy_test` database, creates/drops only the application tables there, and rolls each test back. The fixture refuses database names that do not contain `test`, to avoid accidentally dropping tables from the development database:

```powershell
cd infra
docker compose up -d db
# Create an isolated test database (only needed once).
docker compose exec -T db createdb -U swafy swafy_test
cd ../apps/api
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
$env:TEST_DATABASE_URL = "postgresql+psycopg://swafy:swafy-dev-password@localhost:5432/swafy_test"
pytest
ruff check src tests
ruff format --check src tests
```

The tests use `Base.metadata.create_all()` only against the test database. Production schema changes must go through Alembic migrations.
