# Nextbin.in - Automation and Monitoring Server

A robust, modular, and resilient automation server built with Python, FastAPI, SQLite (WAL mode), and Huey. It is designed to run efficiently inside a mobile Termux terminal as a lifetime local server, surviving network disconnections and system reboots without losing queued background works.

---

## Key Features

1. **Modular Architecture**: Built as a modular monolith, allowing you to add integration channels like WhatsApp, Discord, or Telegram in the `app/modules/` directory without affecting core services.
2. **Resilient Background Tasks**: Uses **Huey** backed by SQLite to queue background tasks (e.g., polling Instagram chats, check monitoring status). The task states are stored on disk (`data/huey_queue.db`) rather than RAM, guaranteeing recovery on crash or restart.
3. **Database Concurrency (WAL Mode)**: Enforces SQLite **Write-Ahead Logging (WAL)** mode. This allows the API server and the background workers to read/write concurrently without "database is locked" errors.
4. **Credential Security**: Symmetric encryption (AES-256 via Fernet) secures third-party credentials (like Instagram passwords) stored in the database.
5. **Instagram Session Persistence**: Serializes Instagram session cookies in SQLite via `instagrapi` to bypass repetitive login attempts, preventing account suspensions.

---

## Directory Structure

```text
/ (Project Root)
├── app/
│   ├── main.py                 # FastAPI Application Entrypoint
│   ├── core/                   # Global Configs, DB setups, Encryption & Security
│   ├── models/                 # Database tables registration (Base, User)
│   ├── schemas/                # Input/Output validation (Pydantic models)
│   ├── api/                    # Endpoints Router (Auth, Projects monitoring, Instagram)
│   ├── workers/                # Background Huey task worker configuration
│   └── modules/                # Automation integration modules
│       ├── base.py             # Abstract base class for automation channels
│       ├── instagram/          # Instagram API client, models & background tasks
│       ├── monitoring/         # Project pinger, SSL checker & metrics loggers
│       └── blog/               # RSS/feed content parsing and notifications
├── scripts/
│   └── start_termux.sh         # Auto-boot runner script for Android Termux
├── requirements.txt            # Python Dependencies
├── .env.example                # Configuration template
└── README.md                   # This instruction file
```

---

## Installation & Setup

### 1. Locally on Windows

1. Clone or navigate to the repository directory.
2. Create and activate a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
4. Generate the `.env` file from the example:
   ```powershell
   python -c "import secrets; from cryptography.fernet import Fernet; jwt_key = secrets.token_hex(32); enc_key = Fernet.generate_key().decode(); content = open('.env.example').read().replace('your-super-secret-jwt-key-change-this-in-production', jwt_key).replace('your-fernet-encryption-key-for-storing-credentials-securely', enc_key); open('.env', 'w').write(content)"
   ```
5. Run the API Server:
   ```powershell
   uvicorn app.main:app --reload
   ```
6. Run the Huey Worker (in a separate terminal inside virtualenv):
   ```powershell
   python -m huey.bin.huey_consumer app.workers.tasks.huey -w 2 -k thread
   ```

### 2. On Android via Termux

1. Install Termux (from F-Droid or GitHub, avoid Play Store as it is outdated).
2. Open Termux and install system prerequisites (important for compiling Python packages like `cryptography` and `bcrypt`):
   ```bash
   pkg update && pkg upgrade
   pkg install python clang make openssl libffi pkg-config
   ```
3. Navigate to the project folder, run setup, and boot the server in one go:
   ```bash
   chmod +x scripts/start_termux.sh
   ./scripts/start_termux.sh
   ```
This script will initialize your virtual environment, install requirements, verify `.env`, start both Uvicorn and the Huey consumer in the background, and pipe execution logs to the `logs/` directory.

---

## How Resilience & Self-Healing Works

* **Offline Robustness**: If the phone loses network connection, tasks that communicate with external APIs (like checking project health or replying to an Instagram chat) will throw errors. Huey traps these errors and utilizes our retry decorator:
  ```python
  @huey.task(retries=3, retry_delay=30, backoff=2)
  ```
  This automatically reschedules the execution with exponential delays (30 seconds -> 60 seconds -> 120 seconds).
* **System Restart Recovery**: If the device runs out of battery, restarts, or Termux is terminated, Huey's SQLite queue file (`data/huey_queue.db`) preserves all tasks that were pending. When `./scripts/start_termux.sh` is executed again, the worker resumes executing these pending tasks immediately.