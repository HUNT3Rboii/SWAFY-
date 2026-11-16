# Vision Worker Architecture Summary

## File Connections

**Core Flow:**
1. `classify.py` - Main entry point that:
   - Loads config from environment variables
   - Selects provider (stub, gemini, or groq)
   - Calls provider.classify()
   - Validates output against schema.json
   - Returns ClassificationResult or unavailable on error/invalid output

2. `result.py` - Defines ClassificationResult type and validates against schema.json:
   - status: "safe", "unsafe", "unavailable" (fail-closed)
   - category: one of 5 frozen categories + "unknown" (worker-only)
   - confidence: 0.0-1.0
   - reason: explanatory string
   - Validates against services/vision-worker/schema.json

3. `providers/stub.py` - Stub provider for testing:
   - Returns canned results based on STUB_MODE env var
   - Modes: safe, unsafe, unavailable, error
   - Never raises during normal operation (error mode raises for testing)

4. `config.py` - Configuration handling:
   - Reads env vars with defaults
   - VISION_PROVIDER defaults to "stub"
   - STUB_MODE defaults to "safe"
   - No API keys required (empty = stub)

5. `log_setup.py` - Logging configuration:
   - Sets up root logger with format "%(asctime)s %(levelname)s [vision-worker] %(message)s"
   - Logs go to stdout

6. `__main__.py` - Service entry point:
   - Creates config, sets up logging
   - Logs startup info
   - Sleeps forever (for container health checks)

## Diagram: classify() Flow
```
classify(image_path) 
    → loads Config 
    → _build_provider(cfg) 
        → stub (if no keys) 
        → gemini (if VISION_PROVIDER=gemini and key) 
        → groq (if VISION_PROVIDER=groq and key) 
    → provider.classify() 
    → validate_dict() 
        → jsonschema.validate() 
    → ClassificationResult (valid) 
        or _unavailable() (invalid/error) 
    → returns result
```

## Key Contracts
- **Fail closed**: Any error/exception → status=unavailable (never safe)
- **No real API keys in code**: Use env vars (.env.example)
- **Stub mode**: STUB_MODE=safe|unsafe|unavailable|error
- **Schema validation**: All results must match schema.json
- **No boolean return**: status is one of three values, never boolean

## Compliance Check Against CLAUDE.md

### ✅ What's Done (Matches CLAUDE.md):
1. ✅ **Service config from environment variables** (config.py)
2. ✅ **JSON schema committed in services/vision-worker/** (schema.json)
3. ✅ **classify() with fail-closed behavior** (classify.py lines 45-64)
4. ✅ **Stub provider with canned results** (stub.py, STUB_MODE options)
5. ✅ **Tests covering safe/unsafe/unavailable/mode** (test_stub.py)
6. ✅ **Dockerfile with non-root user** (Dockerfile lines 17-18)
7. ✅ **Local docker-compose.yml (folder only)** (docker-compose.yml)
8. ✅ **No real API keys in code** (config.py, .env.example)
9. ✅ **Tests generate images with Pillow** (conftest.py)
10. ✅ **.gitignore blocks eval/photos/ only** (not global *.jpg)
11. ✅ **Branch: abir/AI (created from main)** - not done yet (need to create)
12. ✅ **Commits start with "AI-1:"** - not done yet (need to create)

### ❌ What's Missing:
1. ❌ **Branch creation**: Need to create `abir/AI` branch from main
2. ❌ **Git commits**: Need to create commits with "AI-1:" prefix
3. ❌ **Tests for preprocess()** (Phase 2) - not implemented yet
4. ❌ **Tests for actual classify() with stub modes** - need to verify all modes work

### ⚠️ Rules Check:
1. ✅ **Only edit services/vision-worker/** - All files are in correct folder
2. ✅ **No edits to docs/, root compose, other services** - All files are in vision-worker
3. ✅ **No global image rules in .gitignore** - Only blocks eval/photos/ folder
4. ✅ **No Phase 2 work slipped in** - Only Phase 1 files exist
5. ✅ **No wrong file names** - All files match CLAUDE.md expectations
6. ✅ **No global *.jpg/.png ignore** - Only eval/photos/ is ignored
7. ✅ **Dockerfile non-root user** - Uses appuser (Dockerfile line 17-18)
8. ✅ **Service starts cleanly without API key** - Uses stub provider by default

## Test Plan (Step 4)
The tests exist and should pass. Based on test files:
- `test_result.py`: Validates schema and result types
- `test_stub.py`: Tests all stub modes and fail-closed behavior
- `test_config.py`: Tests config defaults and stub mode selection

Need to run tests to verify they pass, but first need to create the branch and commit structure.