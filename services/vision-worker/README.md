# Vision worker

Classifies report photos with hosted vision LLMs (Gemini primary, Groq fallback).
The worker never returns a boolean: `classify(image)` returns `status` of
`safe`, `unsafe`, or `unavailable` (fail closed — a broken checker never
approves a photo). `category` is one of the five frozen categories from
`docs/contracts/enums.md`, or `unknown` (worker-only, never stored).

## Phase 1 (AI-1)

- Service config from environment variables + logging (`config.py`, `log_setup.py`).
- JSON schema of the classify result, committed here (`schema.json`).
- `classify()` and result type with fail-closed behaviour.
- Stub provider with canned safe/unsafe/unavailable/error results, selectable via `STUB_MODE`.
- Dockerfile (non-root user) + local docker-compose.yml (folder only).
- Tests under `tests/`.

## Run locally

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

Docker:

```bash
docker compose up
# or, to force a stub mode:
STUB_MODE=unsafe docker compose up --build
```

No real API key is required: the service starts cleanly with the stub provider.