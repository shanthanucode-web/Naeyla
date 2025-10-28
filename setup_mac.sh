#!/bin/bash
# NAEYLA-XS Setup Script for M1/M2 MacBook (8GB RAM)

set -e  # Exit on error

echo "=== NAEYLA-XS Setup ==="
echo ""

# Check if running on Apple Silicon
ARCH=$(uname -m)
if [[ "$ARCH" != "arm64" ]]; then
    echo "❌ Error: This script requires Apple Silicon (M1/M2/M3)"
    echo "   Detected architecture: $ARCH"
    exit 1
fi

echo "✅ Detected Apple Silicon ($ARCH)"

# Check RAM
RAM_GB=$(sysctl hw.memsize | awk '{print int($2/1024/1024/1024)}')
echo "💾 System RAM: ${RAM_GB}GB"

# Check Python version
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "🐍 Python version: $PYTHON_VERSION"

# Install dependencies
echo "📥 Installing Python packages..."
pip install --quiet --upgrade pip
pip install --quiet mlx mlx-lm transformers huggingface-hub

# Install Playwright
echo "🌐 Installing Playwright..."
pip install --quiet playwright fastapi uvicorn python-multipart
playwright install chromium

# Verify MLX
echo ""
echo "🔍 Verifying MLX installation..."
python -c "import mlx.core as mx; assert mx.metal.is_available(), 'Metal not available'; print('✅ MLX + Metal backend working')"

echo ""
echo "=== Setup Complete ==="
echo ""
