#!/usr/bin/env bash

# Exit immediately if any command fails
set -e

# Setup directories
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

mkdir -p data logs

echo "=================================================="
echo " Starting Nextbin.in Termux Automation Suite      "
echo "=================================================="

# Check if python3 is installed
if ! command -v python &> /dev/null; then
    echo "[ERROR] Python is not installed. Run: pkg install python"
    exit 1
fi

# Set up python virtual environment
if [ ! -d "venv" ]; then
    echo "[INFO] Creating virtual environment (venv)..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/Update requirements
echo "[INFO] Syncing dependencies from requirements.txt..."
# In Termux, compiling cryptography and bcrypt can require clang. We will use --prefer-binary if available or let it compile.
pip install --upgrade pip
pip install -r requirements.txt

# Enforce secure configurations if not present
if [ ! -f ".env" ]; then
    echo "[INFO] Generating .env with fresh encryption credentials..."
    python -c "import secrets; from cryptography.fernet import Fernet; jwt_key = secrets.token_hex(32); enc_key = Fernet.generate_key().decode(); content = open('.env.example').read().replace('your-super-secret-jwt-key-change-this-in-production', jwt_key).replace('your-fernet-encryption-key-for-storing-credentials-securely', enc_key); open('.env', 'w').write(content)"
fi

echo "[INFO] Starting processes..."

# PIDs files tracking
API_PID_FILE="data/api.pid"
WORKER_PID_FILE="data/worker.pid"

# Function to clean up background processes on script exit
cleanup() {
    echo ""
    echo "[INFO] Stopping processes..."
    
    if [ -f "$API_PID_FILE" ]; then
        API_PID=$(cat "$API_PID_FILE")
        if kill -0 "$API_PID" 2>/dev/null; then
            echo "Stopping FastAPI API server (PID: $API_PID)..."
            kill "$API_PID"
        fi
        rm -f "$API_PID_FILE"
    fi
    
    if [ -f "$WORKER_PID_FILE" ]; then
        WORKER_PID=$(cat "$WORKER_PID_FILE")
        if kill -0 "$WORKER_PID" 2>/dev/null; then
            echo "Stopping Huey Background Worker (PID: $WORKER_PID)..."
            kill "$WORKER_PID"
        fi
        rm -f "$WORKER_PID_FILE"
    fi
    
    echo "Nextbin.in server has been stopped."
    exit 0
}

# Trap Ctrl+C (SIGINT) and exit signals to trigger cleanup
trap cleanup SIGINT SIGTERM EXIT

# 1. Start FastAPI application using Uvicorn
echo "[INFO] Starting Uvicorn API Server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 > logs/api.log 2>&1 &
echo $! > "$API_PID_FILE"
echo "  -> API server is running on http://localhost:8000 (PID: $(cat "$API_PID_FILE"))"

# 2. Start Huey background tasks consumer
# -w: worker thread count, -k: worker type (thread is recommended for Termux to conserve memory)
echo "[INFO] Starting Huey background task worker..."
python -m huey.bin.huey_consumer app.workers.tasks.huey -w 2 -k thread > logs/worker.log 2>&1 &
echo $! > "$WORKER_PID_FILE"
echo "  -> Background worker started (PID: $(cat "$WORKER_PID_FILE"))"

echo "=================================================="
echo "Nextbin.in is running. Press Ctrl+C to shut down."
echo "Check logs in logs/api.log and logs/worker.log."
echo "=================================================="

# Keep script running to monitor children and catch interrupt signal
while true; do
    # Verify child processes are still running
    if [ -f "$API_PID_FILE" ]; then
        if ! kill -0 $(cat "$API_PID_FILE") 2>/dev/null; then
            echo "[WARNING] FastAPI API server crashed! Check logs/api.log"
            break
        fi
    fi
    if [ -f "$WORKER_PID_FILE" ]; then
        if ! kill -0 $(cat "$WORKER_PID_FILE") 2>/dev/null; then
            echo "[WARNING] Huey Background Worker crashed! Check logs/worker.log"
            break
        fi
    fi
    sleep 3
done
