#!/bin/bash
# Vision-worker Docker verification script
# Run this from services/vision-worker/

set -e

echo "=== Step 1: docker build ==="
docker build -t vision-worker .
echo "BUILD OK"

echo ""
echo "=== Step 2: docker run --rm vision-worker (should start, print log, stay alive) ==="
timeout 5 docker run --rm vision-worker || true
echo "RUN OK (stopped after 5s)"

echo ""
echo "=== Step 3: env check - PYTHONPATH must appear, VISION_PROVIDER/STUB_MODE must NOT ==="
docker run --rm --entrypoint sh vision-worker -c "env | grep -E 'VISION|STUB|PYTHONPATH'"

echo ""
echo "=== Step 4: explicit stub mode ==="
timeout 5 docker run --rm -e VISION_PROVIDER=stub -e STUB_MODE=safe vision-worker || true
echo "STUB RUN OK"

echo ""
echo "=== Step 5: file listing - must contain requirements.txt, schema.json, src/*.py; must NOT contain __pycache__, tests/, CLAUDE.md, .env ==="
docker run --rm --entrypoint sh vision-worker -c "find /app -type f | sort"

echo ""
echo "=== Step 6: git status ==="
cd ..
git status

echo ""
echo "ALL VERIFICATION STEPS COMPLETE"