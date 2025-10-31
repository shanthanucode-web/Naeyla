# NAEYLA-XS

**Personal AI Assistant running locally on M1 MacBook Air (8GB RAM)**

Naeyla is a 1.5B parameter language model (Qwen 2.5) running entirely on-device using Apple's MLX framework. No cloud, no external APIs, just a personal AI companion.

## Features

- **Three personality modes**: Companion, Advisor, Guardian
- **Beautiful web interface** with real-time chat
- **Runs locally** on M1/M2 MacBook (8GB RAM minimum)
- **Fast inference** using Apple Silicon optimization
- Browser automation (coming soon)
- Episodic memory system (coming soon)
- Personal learning via LoRA fine-tuning (coming soon)

## Tech Stack

- **Model**: Qwen 2.5-1.5B-Instruct (4-bit quantized)
- **Framework**: MLX (Apple's ML framework)
- **Backend**: FastAPI with token auth
- **Frontend**: Tauri (native app)
- **Platform**: macOS (Apple Silicon)

## Setup

### Requirements
- macOS with Apple Silicon (M1/M2/M3)
- 8GB+ RAM
- Python 3.11+

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
pip install fastapi uvicorn playwright python-multipart

Download the model (1.5GB)
mkdir -p models
huggingface-cli download Qwen/Qwen2.5-1.5B-Instruct --local-dir models/qwen2.5-1.5b

Install Playwright browser
playwright install chromium

### Configuration

Create '.env' in the root directory:
echo "NAEYLA_TOKEN=$(openssl rand -base 64 32)">.env

### Running Naeyla

Activate virtual environment
source venv/bin/activate

**Terminal 1 - Backend:**
Start the server
source venv/bin/activate
uvicorn app.server_secure:app --host 127.0.0.1 --port 7861 --reload

**Terminal 2 - Frontend:**
cd tauri-app/naeyla-native
npm install
npm run tauri dev

## Project Status

**Week 1 - Day 1**: Complete
- Model loading and inference working
- Web interface functional
- Three personality modes active

**Next**: Browser automation + memory system

## Philosophy

Naeyla is an attempt to make a **personal cognitive organism**. She learns from one user and evolves with them. This is an experiment in building a unified AI consciousness that perceives, reasons, acts, and remembers within a single neural architecture.

## Architecture

naeyla-xs/
├── app/ # Backend
│ ├── server_secure.py # Secure FastAPI server
│ └── .env # Token (git ignored)
├── tauri-app/naeyla-native/ # Native frontend
│ ├── src/
│ │ ├── main.ts
│ │ └── vite-env.d.ts
│ └── .env.local # Frontend token (git ignored)
├── models/ # AI model code
├── dsl/ # Action grammar
├── env/ # Browser control
├── memory/ # Episodic memory
└── trace/ # Training data collection


## Security

- Tokens stored in `.env` files (git ignored)
- Backend validates auth on every request
- Frontend injects token via environment variables
- code is secure


## Credits

Built by Shanthanu with guidance from Perplexity AI.  
Inspired by the vision of personal, lifelong AI companions and Jarvis.

---

*"Cultivating an AI conscience."*
