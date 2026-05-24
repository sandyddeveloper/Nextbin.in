import os
from pathlib import Path
from typing import List
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve paths relative to the project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "Nextbin.in Automation Server"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Server Bind Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Security Keys
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ENCRYPTION_KEY: str  # Fernet key for encrypting sensitive credentials
    DEPLOY_SECRET: str = "mysecret123"
    CLOUDFLARE_TUNNEL_NAME: str = ""  # Custom Cloudflare Tunnel Name (e.g. 'nila-tunnel')

    # Database Configuration
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/nextbin.db"

    # Background Queue Database Path
    QUEUE_DB_PATH: str = "./data/huey_queue.db"

    # Directory for local persistence (e.g. databases, logs, Instagram sessions)
    DATA_DIR: str = "./data"

    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # Module Defaults
    INSTAGRAM_TIMEOUT: int = 30
    INSTAGRAM_MAX_RETRIES: int = 3

    # Nila Gravity & OneSignal Configuration
    EMAIL_USER: str = ""
    EMAIL_PASS: str = ""
    ONESIGNAL_APP_ID: str = ""
    ONESIGNAL_API_KEY: str = ""
    NEXT_PUBLIC_API_URL: str = "http://localhost:3000"

    @property
    def sqlite_db_path(self) -> Path:
        # Helper to extract SQLite file path from DATABASE_URL
        if self.DATABASE_URL.startswith("sqlite"):
            db_path_str = self.DATABASE_URL.split(":///")[1]
            return Path(db_path_str)
        return Path("./data/nextbin.db")

settings = Settings()

# Ensure target data directories exist
os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(os.path.dirname(settings.QUEUE_DB_PATH), exist_ok=True)
