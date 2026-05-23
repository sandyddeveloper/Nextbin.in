#!/bin/bash

# Force exit if any command fails (except those we handle)
set -e

PROJECT_DIR="/data/data/com.termux/files/home/Nextbin.in"
cd "$PROJECT_DIR"

echo "📥 [Deploy] Pulling latest code from origin main..."
git pull origin main

# Update python environment
if [ -d "venv" ]; then
    echo "🐍 [Deploy] Activating virtual environment..."
    source venv/bin/activate
    
    echo "📦 [Deploy] Installing/updating dependencies..."
    pip install -r requirements.txt
fi

# We schedule the restart sequence in a detached subshell.
# This allows the FastAPI webhook process that triggered us to complete
# and return an HTTP 200 to the client (GitHub) before it is killed.
echo "🔄 [Deploy] Scheduling detached restart..."
nohup bash -c "
  echo '⏳ Waiting for FastAPI response to settle...'
  sleep 3
  
  echo '🛑 Stopping old NILA processes...'
  # Find and kill the nila.py process (which will clean up its child FastAPI and Huey processes)
  pkill -f 'python.*nila.py' || true
  pkill -f uvicorn || true
  pkill -f 'huey.bin.huey_consumer' || true
  sleep 2
  
  echo '🚀 Starting NILA service in background...'
  # Run nila.py to boot both API and Huey worker processes
  nohup python nila.py > logs/nila.log 2>&1 &
  
  # Restart Cloudflare tunnel if configured
  echo '🌐 Restarting cloudflared tunnel...'
  pkill cloudflared || true
  sleep 1
  nohup cloudflared tunnel --url http://localhost:8000 > logs/cloudflared.log 2>&1 &
  
  # Wait for cloudflared to establish the tunnel
  sleep 6
  CF_URL=$(grep -oE "https://[a-zA-Z0-9-]+\.trycloudflare\.com" logs/cloudflared.log | head -n 1 || true)
  if [ ! -z "$CF_URL" ]; then
    echo "$CF_URL" > logs/cloudflare_url.txt
    echo "🌐 [Deploy] Public Tunnel URL: $CF_URL"
  else
    echo "⚠️ [Deploy] Could not auto-detect Cloudflare URL in logs/cloudflared.log"
  fi
  
  echo '✅ [Deploy] Restart sequence complete!'
" > logs/deploy_exec.log 2>&1 &

echo "🚀 [Deploy] Webhook deployment processed successfully!"

