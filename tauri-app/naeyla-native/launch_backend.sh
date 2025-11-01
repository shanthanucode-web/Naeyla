#!/bin/bash
cd ~/naeyla-xs
source venv/bin/activate
uvicorn app.server_secure:app --host 127.0.0.1 --port 7861 >/tmp/naeyla_backend.log 2>&1 &
sleep 2
