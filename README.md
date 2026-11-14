# SWAFY

Citizens report city issues (potholes, trash, graffiti, broken lights) with a photo; the municipality tracks and resolves them.

| Folder | What |
|---|---|
| `apps/mobile` | Citizen app (Expo) |
| `apps/dashboard` | Municipal dashboard |
| `apps/api` | Backend API |
| `services/vision-worker` | AI photo check |
| `packages/api-client` | Typed API client, generated from the contract |
| `packages/map-*` | Shared map components |
| `docs/contracts` | OpenAPI contract and shared enums |
| `infra` | Docker compose dev stack |

## Run the dev stack

You need [Docker Desktop](https://www.docker.com/products/docker-desktop/).

```bash
git clone https://github.com/HUNT3Rboii/SWAFY-.git
cd SWAFY-/infra
cp .env.example .env
docker compose up
```

| Service | Address |
|---|---|
| Mock API (answers with the contract's examples) | http://localhost:4010 |
| PostgreSQL + PostGIS | `localhost:5432` (user/password in `infra/.env`) |
| MinIO storage | http://localhost:9000, console http://localhost:9001 |

MinIO gets two buckets: `quarantine` (private, photos waiting for the AI check) and `public` (approved photos).

The real API and worker are not built yet. When they are:

```bash
cp env/api.env.example env/api.env
cp env/worker.env.example env/worker.env
docker compose --profile api --profile worker up
```

Stop with `Ctrl+C`. To wipe the database and photos: `docker compose down -v`.

## Mock or real API

Apps choose with `API_BASE_URL`:

| | `API_BASE_URL` |
|---|---|
| Mock API | `http://<host>:4010` |
| Real API | `http://<host>:8000/api/v1` |

**On a real phone, `localhost` is the phone itself.** Use your laptop's Wi-Fi IP instead
(Windows: `ipconfig`, Mac: `ipconfig getifaddr en0`, Linux: `hostname -I`), for example
`http://192.168.1.20:4010`. Phone and laptop must be on the same Wi-Fi.

## Secrets

Only `*.env.example` files are committed; every `.env` file is git-ignored.
Real API keys (Gemini, Groq) are shared privately, never in the repo.

## API client

`packages/api-client` is generated from `docs/contracts/openapi.yaml`. After changing the contract:

```bash
cd packages/api-client
npm install
npm run generate
```

Commit the updated `src/schema.ts`. CI fails if it doesn't match the contract.

```ts
import { createApiClient } from '@swafy/api-client';

const api = createApiClient({ baseUrl: API_BASE_URL, getToken: () => accessToken });
const { data, error } = await api.GET('/reports/mine');
```

## Team rules

See [docs/WORKING_AGREEMENT.md](docs/WORKING_AGREEMENT.md).
