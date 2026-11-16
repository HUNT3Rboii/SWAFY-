# Web image: dashboard build served by Caddy, which also proxies the API and photos.
# Build from the repo root:  docker build -f infra/web/Dockerfile .

FROM node:22-alpine AS dashboard
WORKDIR /app
COPY apps/dashboard/ ./
# The dashboard calls the API on the same address, so no CORS is needed.
ENV VITE_API_BASE_URL=/api/v1
RUN if [ -f package.json ]; then \
      npm ci && npm run build && mv dist /out; \
    else \
      mkdir -p /out && \
      printf '<!doctype html><meta charset="utf-8"><title>SWAFY</title><p>SWAFY is running. The dashboard is not built yet.</p>\n' > /out/index.html; \
    fi

FROM caddy:2.10.2-alpine
COPY infra/web/Caddyfile /etc/caddy/Caddyfile
COPY --from=dashboard /out /srv/dashboard
