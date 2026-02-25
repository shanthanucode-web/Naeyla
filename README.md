# NAEYLA-XS

**Personal AI Assistant running locally on Apple Silicon**

Naeyla is a 1.5B parameter language model (Qwen 2.5) running entirely on-device using Apple's MLX framework. No cloud, no external APIs, just a personal AI companion.

## Features

- **Three personality modes**: Companion, Advisor, Guardian
- **Native desktop UI** with real-time chat (Tauri + Vite)
- **Runs locally** on Apple Silicon with MLX acceleration
- **Browser automation** via Playwright (experimental)
- **Memory store scaffolding** (SQLite + embeddings; not yet used in chat responses)

## Tech Stack

- **Model**: Qwen 2.5-1.5B-Instruct (4-bit quantized)
- **Framework**: MLX (Apple's ML framework)
- **Backend**: FastAPI with token auth
- **Frontend**: Tauri (native app)
- **Platform**: macOS (Apple Silicon)

## Quick Start

Run backend + frontend together:
```bash
npm run dev
```

Or directly:
```bash
./run_dev.sh
```

## Setup

### Requirements
- macOS with Apple Silicon (M1/M2/M3)
- 8GB+ RAM
- Python 3.11+
- Node.js 18+ and npm
- Rust toolchain (for Tauri)

### Installation

Clone the repo
git clone https://github.com/shanthanucode-web/Naeyla.git
cd naeyla-xs

### Backend Setup
Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

Install dependencies
pip install mlx mlx-lm transformers huggingface-hub
pip install fastapi uvicorn playwright python-multipart python-dotenv
pip install sentence-transformers numpy

Download the model (1.5GB)
mkdir -p models
huggingface-cli download Qwen/Qwen2.5-1.5B-Instruct --local-dir models/qwen2.5-1.5b

Install Playwright browser
playwright install chromium

### Configuration

Create '.env' in the root directory:
echo "NAEYLA_TOKEN=$(openssl rand -base 64 32)">.env

Create `tauri-app/naeyla-native/.env.local`:
echo "VITE_NAEYLA_TOKEN=your_token_here" > tauri-app/naeyla-native/.env.local
The frontend token must match `NAEYLA_TOKEN`.

### Running Naeyla

**Option A (recommended):**
```bash
npm run dev
```

**Option B (manual, two terminals):**

Terminal 1 - Backend
Start the server
source venv/bin/activate
uvicorn app.server_secure:app --host 127.0.0.1 --port 7861 --reload

Terminal 2 - Frontend
cd tauri-app/naeyla-native
npm install
npm run tauri dev

## Project Status

Active development. Core chat flow and UI are working; browser actions are experimental; memory storage exists but is not fully integrated into chat responses.

## Philosophy

Naeyla is an attempt to make a **personal cognitive organism**. She learns from one user and evolves with them. This is an experiment in building a unified AI consciousness that perceives, reasons, acts, and remembers within a single neural architecture.

## Architecture

See `ARCHITECTURE.md` for a concise codebase tour and a runtime sequence diagram.


## Security

- Tokens stored in `.env` files (git ignored)
- Backend validates auth on every request
- Frontend injects token via environment variables


## Credits

Built by Shanthanu with guidance from Perplexity AI.  
Inspired by the vision of personal, lifelong AI companions and Jarvis.

---

*"Cultivating an AI conscience."*
