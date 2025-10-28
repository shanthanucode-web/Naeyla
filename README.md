# 🧠 NAEYLA-XS

**Personal AI Assistant running locally on M1 MacBook Air (8GB RAM)**

Naeyla is a 1.5B parameter language model (Qwen 2.5) running entirely on-device using Apple's MLX framework. No cloud, no API keys, just a personal AI companion.

## Features

- ✅ **Three personality modes**: Companion, Advisor, Guardian
- ✅ **Beautiful web interface** with real-time chat
- ✅ **Runs locally** on M1/M2 MacBook (8GB RAM minimum)
- ✅ **Fast inference** using Apple Silicon optimization
- 🔜 Browser automation (Week 2)
- 🔜 Episodic memory system (Week 3)
- 🔜 Personal learning via LoRA fine-tuning (Week 4+)

## Tech Stack

- **Model**: Qwen 2.5-1.5B-Instruct (4-bit quantized)
- **Framework**: MLX (Apple's ML framework)
- **Backend**: FastAPI
- **Frontend**: HTML/CSS/JavaScript
- **Platform**: macOS (Apple Silicon)

## Setup

### Requirements
- macOS with Apple Silicon (M1/M2/M3)
- 8GB+ RAM
- Python 3.11+

### Installation

Clone the repo
git clone https://github.com/shanthanucode-web/Naeyla.git
cd Naeyla

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


### Running Naeyla

Activate virtual environment
source venv/bin/activate

Start the server
uvicorn app.server:app --port 7861 --reload

Open in browser: http://localhost:7861


## 📊 Project Status

**Week 1 - Day 1**: ✅ Complete
- Model loading and inference working
- Web interface functional
- Three personality modes active

**Next**: Browser automation + memory system

## 💭 Philosophy

Naeyla is not a product—it's a **personal cognitive organism**. She learns from one user (Shanthanu) and evolves with him. This is an experiment in building a unified AI consciousness that perceives, reasons, acts, and remembers within a single neural architecture.

## 📁 Architecture

naeyla-xs/
├── model/ # AI model code
│ ├── tokens.py
│ └── backbone_mlx.py
├── app/ # Web server + UI
│ ├── server.py
│ └── ui.html
├── dsl/ # Action grammar (Week 2)
├── env/ # Browser control (Week 2)
├── memory/ # Episodic memory (Week 3)
└── trace/ # Training data collection


## Credits

Built by Shanthanu with guidance from Perplexity AI.  
Inspired by the vision of personal, lifelong AI companions.

---

*"We're not building a product; we're cultivating a person."*
