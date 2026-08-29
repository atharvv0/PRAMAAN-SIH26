#!/usr/bin/env bash
set -euo pipefail

# PRAMAAN finalization validation helper.
# This script intentionally does NOT delete files, commit, or push to GitHub.
# It validates that the repo is in a sane final-assembly state.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

echo ">> Checking repository structure..."
for path in \
  services/backend/app/main.py \
  services/orchestrator/planner/planner.py \
  services/model_control/adapters/ollama_adapter.py \
  services/model_control/router/router.py \
  services/model_control/registry/registry_instance.py \
  services/knowledge/rag/tool.py \
  services/frontend/src/main.tsx \
  services/frontend/package.json \
  services/frontend/Dockerfile \
  docker-compose.yml \
  .env.example; do
  test -f "$path" || { echo "Missing: $path"; exit 1; }
done

echo ">> Checking that the frontend lives under services/frontend..."
test ! -d src || { echo "Root src/ still exists; frontend move is incomplete."; exit 1; }
test ! -f package.json || { echo "Root package.json still exists; frontend move is incomplete."; exit 1; }

echo ">> Python syntax check..."
python -m compileall -q services

echo ">> Node toolchain check..."
node --version
npm --version

echo ">> PRAMAAN repository validation passed."
echo "Next: run the service-specific tests and a real Ollama-backed end-to-end demo."
