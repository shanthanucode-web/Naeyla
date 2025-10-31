#!/bin/bash
# Auto-start Naeyla backend

BACKEND_DIR="$HOME/naeyla-xs"
VENV_PATH="$BACKEND_DIR/venv/bin/activate"

cd "$BACKEND_DIR"

# Activate venv
source "$VENV_PATH"

# Start server
uvicorn app.server_secure:app --host 127.0.0.1 --port 7861
