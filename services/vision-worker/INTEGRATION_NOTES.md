# Integration notes: vision-worker

Changes this service needs **outside** `services/vision-worker/`. I do not edit
those folders myself (team rule); each item below is a request for its owner
(open as a `type:integration` issue).

## 1. Schema under `docs/contracts/` (AI-1 "done when")

The AI-1 issue asks for the classify schema under `docs/contracts/`.
The source of truth today is `services/vision-worker/schema.json` (the worker
and its tests load it from there). It is aligned with BE-1: it equals the
decision fields of `PhotoCheckResultRequest` in `docs/contracts/openapi.yaml`
(everything except `lease_token`, which the BE-4 transport layer adds).

Request: copy it to `docs/contracts/vision-classify.schema.json` (owner of
`docs/contracts/`), or simply point to `PhotoCheckResultRequest` in
`openapi.yaml`, which already says the same thing. Contract summary:

| field        | type           | values                                                              |
|--------------|----------------|---------------------------------------------------------------------|
| `outcome`    | string         | `safe` / `unsafe` / `unavailable` (never a boolean)                  |
| `category`   | string         | `pothole`, `trash`, `graffiti`, `broken_light`, `other`, `unknown`   |
| `confidence` | number or null | 0 to 1; `null` when `unavailable`                                    |
| `reason`     | string         | 1 to 2000 chars                                                      |
| `provider`   | string         | `stub`, `gemini`, `groq`, or `none` (no provider could run)          |

Rules: `unsafe` and `unavailable` always use category `unknown`.
Mapping to `photo_state` (done by the API): `safe` -> `approved`,
`unsafe` -> `rejected`, `unavailable` -> stays `pending_check` (retried,
**never** published).

## 2. Root compose (OPS-2, already merged)

`infra/docker-compose.yml` already has a `worker` service (profile `worker`)
that builds this folder and reads `infra/env/worker.env`. Nothing to change
there for AI-1: with no `VISION_PROVIDER` / `STUB_MODE` in that file the
worker starts with the stub in `safe` mode and logs a startup warning.

Request for the owner of `infra/env/worker.env.example`: add these lines so
the options are visible:

```
# stub | gemini | groq  (stub approves everything: dev only)
VISION_PROVIDER=stub
# stub only: safe | unsafe | unavailable | error
STUB_MODE=safe
LOG_LEVEL=info
```

`infra/env/worker.prod.env.example` should set `VISION_PROVIDER=gemini` once
AI-2 lands. A real provider with a missing key gives `unavailable` (fail
closed), never `safe`.

## 3. CI pytest job (`.github/workflows/ci-services-vision-worker.yml`)

The current job only echoes a message. Suggested steps (owner of `.github/`):

```yaml
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install
        working-directory: services/vision-worker
        run: pip install -r requirements-dev.txt
      - name: Test
        working-directory: services/vision-worker
        run: pytest
```

No secrets are needed: tests use the stub and generate images with Pillow.
