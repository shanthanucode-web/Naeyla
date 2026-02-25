# NAEYLA-XS

**Personal AI Assistant running locally on Apple Silicon**

Naeyla is a 1.5B parameter language model (Qwen 2.5) running entirely on-device using Apple's MLX framework. No cloud, no external APIs — just a personal AI companion.

## Features

- **Three personality modes**: Companion, Advisor, Guardian
- **Native desktop UI** with real-time chat (Tauri + Vite)
- **Runs locally** on Apple Silicon with MLX acceleration
- **Browser automation** via Playwright (experimental)
- **Memory store scaffolding** (SQLite + embeddings; disabled by default)

## Tech Stack

- **Model**: Qwen 2.5-1.5B-Instruct
- **Inference**: MLX (Apple's ML framework)
- **Backend**: FastAPI with token auth
- **Frontend**: Tauri + Vite (native app)
- **Platform**: macOS (Apple Silicon)

## Quick Start

Launch the native app (auto-starts the backend):
```bash
cd tauri-app/naeyla-native
npm run tauri dev
```

Or run both together from the repo root:
```bash
npm run dev
```

## Setup

### Requirements

- macOS with Apple Silicon (M1/M2/M3)
- 8GB+ RAM
- Python 3.11+
- Node.js 18+ and npm
- Rust toolchain (for Tauri)

### 1. Clone

```bash
git clone https://github.com/shanthanucode-web/Naeyla.git
cd Naeyla
```

### 2. Python environment

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install mlx mlx-lm transformers huggingface-hub python-dotenv
pip install fastapi uvicorn playwright python-multipart
pip install sentence-transformers numpy
playwright install chromium
```

### 3. Download the model (~1.5 GB)

```bash
mkdir -p models
huggingface-cli download Qwen/Qwen2.5-1.5B-Instruct --local-dir models/qwen2.5-1.5b
```

### 4. Frontend dependencies

```bash
cd tauri-app/naeyla-native
npm install
cd ../..
```

### 5. Configure tokens

Generate a secret token and write both config files:

```bash
TOKEN=$(openssl rand -base64 32)
echo "NAEYLA_TOKEN=$TOKEN" > .env
echo "VITE_NAEYLA_TOKEN=$TOKEN" > tauri-app/naeyla-native/.env.local
```

Both files are git-ignored. The backend reads `NAEYLA_TOKEN` and the frontend reads `VITE_NAEYLA_TOKEN` — they must match.

## Running Naeyla

**Option A — recommended (auto-starts backend):**

```bash
cd tauri-app/naeyla-native
npm run tauri dev
```

**Option B — manual (two terminals):**

```bash
# Terminal 1: backend
source venv/bin/activate
uvicorn app.server_secure:app --host 127.0.0.1 --port 7861

# Terminal 2: frontend
cd tauri-app/naeyla-native
npm run tauri dev
```

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for a full codebase tour and runtime sequence diagram.

## Runtime Notes

- The native app auto-starts the backend on launch and polls `/health` before sending the first message.
- The MLX model is lazy-loaded on the first chat request to reduce startup time and memory pressure.
- Memory indexing is disabled by default; enable with `NAEYLA_ENABLE_MEMORY=1`.

## Dev Flags

| Flag | Effect |
|------|--------|
| `NAEYLA_EAGER_LOAD=1` | Load model at server startup (not recommended on 8 GB) |
| `NAEYLA_ENABLE_MEMORY=1` | Enable memory system initialisation |
| `NAEYLA_RELOAD=1` | Enable uvicorn auto-reload in `npm run dev` |

## Troubleshooting

- **Backend not responding** — check `naeyla_backend.log` in the repo root.
- **Auth errors** — verify that `NAEYLA_TOKEN` in `.env` matches `VITE_NAEYLA_TOKEN` in `tauri-app/naeyla-native/.env.local`.
- **Model not found** — confirm the model was downloaded to `models/qwen2.5-1.5b`.

## Security

See [SECURITY.md](SECURITY.md) for a full breakdown of the security model, token management, and known limitations.

## Project Status

Active development. Core chat and UI are working; browser automation is experimental; memory storage is scaffolded but not yet wired into chat responses.

## Philosophy

Naeyla is an attempt to build a **personal cognitive organism** — an AI that learns from one person and evolves with them. An experiment in unified perception, reasoning, action, and memory within a single neural architecture.

## Credits

Built by Shanthanu.
Inspired by the vision of personal, lifelong AI companions.

---

*"Cultivating an AI conscience."*
