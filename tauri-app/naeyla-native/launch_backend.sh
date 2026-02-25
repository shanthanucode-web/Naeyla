#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_FILE="$ROOT_DIR/naeyla_backend.log"

if lsof -iTCP:7861 -sTCP:LISTEN -t >/dev/null 2>&1; then
  echo "Backend already running on port 7861."
  exit 0
fi

if [[ ! -f "$ROOT_DIR/venv/bin/activate" ]]; then
  echo "Missing venv at $ROOT_DIR/venv. Create it with:"
  echo "  python3.11 -m venv venv"
  exit 1
fi

cd "$ROOT_DIR"
# shellcheck disable=SC1091
source venv/bin/activate

uvicorn app.server_secure:app --host 127.0.0.1 --port 7861 >"$LOG_FILE" 2>&1 &
sleep 2
