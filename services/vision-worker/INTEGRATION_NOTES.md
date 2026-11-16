# Integration notes: vision-worker

Changes this service needs **outside** `services/vision-worker/`. I do not edit
those folders myself (team rule); each item below is a request for its owner
(open as a `type:integration` issue).

## 1. Schema under `docs/contracts/` (AI-1 "done when")

The AI-1 issue asks for the classify schema under `docs/contracts/`.
The source of truth today is `services/vision-worker/schema.json` (the worker
and its tests load it from there).

Request: copy it to `docs/contracts/vision-classify.schema.json` (owner of
`docs/contracts/`). Until then, backend and mobile can read the file in this
folder. Contract summary:

| field        | type   | values                                                         |
|--------------|--------|----------------------------------------------------------------|
| `status`     | string | `safe` / `unsafe` / `unavailable` (never a boolean)             |
| `category`   | string | `pothole`, `trash`, `graffiti`, `broken_light`, `other`, `unknown` |
| `confidence` | number | 0 to 1                                                         |
| `reason`     | string | non-empty                                                      |

Mapping to the frozen `photo_state` (from `docs/contracts/enums.md`):

- `safe` -> `approved`
- `unsafe` -> `rejected`
- `unavailable` -> stays `pending_check` (retried later, **never** published)

`unknown` is a worker-only category meaning "ask the user to pick". It is never
stored.

## 2. Root compose entry (OPS-2)

Suggested service block for the shared compose file (owner of `infra/` / root
compose). It starts cleanly with no API key (stub provider, safe mode):

```yaml
  vision-worker:
    build: ./services/vision-worker
    environment:
      VISION_PROVIDER: ${VISION_PROVIDER:-stub}
      STUB_MODE: ${STUB_MODE:-safe}
      GEMINI_API_KEY: ${GEMINI_API_KEY:-}
      GROQ_API_KEY: ${GROQ_API_KEY:-}
      LOG_LEVEL: ${LOG_LEVEL:-info}
    restart: unless-stopped
```

No ports: the worker does not serve HTTP. How it receives jobs depends on
BE-4 (not decided yet).

**Production warning:** the default `stub` + `safe` approves every photo
without checking it. The worker logs a WARNING at startup when the stub is on.
Production must set `VISION_PROVIDER=gemini` (once AI-2 lands). A real
provider with a missing key gives `unavailable` (fail closed), never `safe`.

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
