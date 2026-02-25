#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ ! -f "$ROOT_DIR/venv/bin/activate" ]]; then
  echo "Missing venv. Create it with:"
  echo "  python3.11 -m venv venv"
  exit 1
fi

if [[ ! -f "$ROOT_DIR/.env" ]]; then
  echo "Warning: $ROOT_DIR/.env not found. Backend will fail without NAEYLA_TOKEN."
fi

cleanup() {
  if [[ -n "${BACKEND_PID:-}" ]]; then
    kill "$BACKEND_PID" >/dev/null 2>&1 || true
    wait "$BACKEND_PID" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT INT TERM

echo "Starting backend on http://127.0.0.1:7861 ..."
(
  cd "$ROOT_DIR"
  # shellcheck disable=SC1091
  source venv/bin/activate
  if [[ "${NAEYLA_RELOAD:-}" == "1" ]]; then
    uvicorn app.server_secure:app --host 127.0.0.1 --port 7861 --reload
  else
    uvicorn app.server_secure:app --host 127.0.0.1 --port 7861
  fi
) &
BACKEND_PID=$!

sleep 1

echo "Starting frontend (Tauri)..."
cd "$ROOT_DIR/tauri-app/naeyla-native"

if [[ ! -d node_modules ]]; then
  npm install
fi

npm run tauri dev
