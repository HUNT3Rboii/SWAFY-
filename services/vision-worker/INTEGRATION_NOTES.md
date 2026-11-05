# Integration Notes — pytest CI for vision-worker

## What this job does

Runs `pytest` inside the `services/vision-worker/` folder, using the
project's own `pytest.ini` and `requirements-dev.txt`.

## How to run locally (same as CI)

```bash
cd services/vision-worker
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

## Expected test output

All 20+ tests should pass, covering:

- `test_result.py`: schema validation, valid/invalid results, `validate_dict`
- `test_stub.py`: stub safe/unsafe/unavailable modes, provider crash → unavailable,
  never-safe contract
- `test_config.py`: defaults, stub mode selection, provider detection

## CI matrix note

This folder currently uses the **stub provider only** (`VISION_PROVIDER=stub`,
`STUB_MODE=safe` by default). The CI job does not need real API keys — it
validates the full contract (schema, fail-closed behaviour, provider
interface) with the stub.

## What to add later (AI-2+)

- When Gemini/Groq adapters are added, the CI job will need to mock those
  providers or run with real keys in a separate job.
- Evaluation script tests (category accuracy, unsafe precision/recall) can be
  added once `labels.csv` and a tiny fake dataset exist.