import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine
from app.models.base import Base
from app.core.logging import setup_logging
from app.api.v1.api import api_router
from app.core.middleware import RequestIdMiddleware, PlatformValidationMiddleware, SecurityHeadersMiddleware

# Initialize custom API rotating logger
setup_logging("api")
logger = logging.getLogger("nextbin.api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI Lifespan management.
    Initializes database tables on start-up.
    """
    logger.info("Initializing database and starting up nextbin server...")
    
    # SQLite schema initialization (safe and incremental)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    logger.info("Database schema checks completed.")
    yield
    logger.info("Shutting down nextbin server...")

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS configurations
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Custom security and tracking middlewares
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(PlatformValidationMiddleware)
app.add_middleware(RequestIdMiddleware)

# Register API Router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["health"])
async def root_health_check():
    """
    Lightweight health check endpoint.
    """
    return {
        "status": "online",
        "app_name": settings.APP_NAME,
        "debug_mode": settings.DEBUG,
        "engine": "FastAPI + SQLite (WAL)"
    }
