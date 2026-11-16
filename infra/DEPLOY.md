# Deploying SWAFY

SWAFY runs on one machine with Docker (for example a team laptop during the demo).
Phones reach it over HTTPS through a free Cloudflare tunnel.

```
phone ──HTTPS──> Cloudflare tunnel ──> web (Caddy) ──> api, dashboard, photos
                                                         db + MinIO: no open ports
```

Every merge to `main` builds new images and pushes them to GitHub's container registry
(`.github/workflows/deploy.yml`). The machine just pulls them.

## First time

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and clone the repo.
2. Log in to the image registry (the images are private). Create a GitHub token with the
   `read:packages` scope, then:
   ```bash
   docker login ghcr.io -u <your GitHub username>
   ```
3. Create the config files and replace every `CHANGE_ME` (`openssl rand -base64 32` makes good passwords):
   ```bash
   cd infra
   cp prod.env.example prod.env
   cp env/api.prod.env.example env/api.prod.env
   cp env/worker.prod.env.example env/worker.prod.env
   ```
   Passwords must match between `prod.env` and `env/api.prod.env`. Ask the PM for the Gemini and Groq keys.
4. Start:
   ```bash
   docker compose -f docker-compose.prod.yml --env-file prod.env pull
   docker compose -f docker-compose.prod.yml --env-file prod.env up -d
   ```

## Get the HTTPS address

```bash
docker compose -f docker-compose.prod.yml --env-file prod.env logs tunnel | grep trycloudflare
```

Then:
1. Put that address in `env/api.prod.env` (`S3_PUBLIC_ENDPOINT` and `CORS_ORIGINS`) and run the `up -d` command again.
2. Build the release app with `EXPO_PUBLIC_API_BASE_URL=https://<address>/api/v1`.

**The address changes every time the tunnel restarts** (restarting Docker or the laptop counts).
Release apps have the address built in, so: start the stack, build the app, and keep the
laptop running until the demo is over. If it changes, repeat the two steps above.

The dashboard is at the same address. On the laptop itself: http://localhost:8080.

## Update to the latest version

```bash
docker compose -f docker-compose.prod.yml --env-file prod.env pull
docker compose -f docker-compose.prod.yml --env-file prod.env up -d
```

## Backups

Every 24 hours (and each time the stack starts) the database is dumped to `BACKUP_DIR/db`
(last 7 kept) and both photo buckets are copied to `BACKUP_DIR/photos`.
Set `BACKUP_DIR` in `prod.env` to a different disk or a synced folder (OneDrive, Google Drive)
so the backups survive if the laptop dies.

Restore (tested: database and photos come back):

```bash
docker compose -f docker-compose.prod.yml --env-file prod.env stop api worker
sh backup/restore.sh backups/db/<file>.dump
docker compose -f docker-compose.prod.yml --env-file prod.env up -d
```

## Security

- Only Caddy has a port, and only on `127.0.0.1`. The database and MinIO are internal.
- Caddy adds security headers, limits API requests to 1 MB and photo uploads to `MAX_UPLOAD_SIZE` (10 MB).
- Quarantine photos are private; public photos can be opened by URL but the bucket can't be listed.
- CORS: the API only allows `CORS_ORIGINS`. The dashboard is on the same address, so it needs no CORS.

## Where the data lives

All data (database, photos, backups) stays on this machine and `BACKUP_DIR`.
HTTPS ends at Cloudflare, so Cloudflare can see traffic passing through the tunnel.
Check this is acceptable with the professor / municipal contact (issue #5).
