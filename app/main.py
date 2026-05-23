import logging
import os
import hmac
import hashlib
import subprocess
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
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


@app.post("/deploy", tags=["deployment"])
async def trigger_deployment(request: Request):
    """
    CI/CD webhook endpoint. Validates GitHub webhook signature,
    x-secret-key header, or secret query parameter, then executes deploy.sh.
    """
    secret = settings.DEPLOY_SECRET
    
    # 1. Check query parameter
    secret_param = request.query_params.get("secret")
    
    # 2. Check x-secret-key header
    secret_header = request.headers.get("x-secret-key")
    
    # 3. Check GitHub webhook signature (X-Hub-Signature-256)
    github_signature = request.headers.get("X-Hub-Signature-256")
    
    is_valid = False
    
    # Verify via query parameter or header
    if (secret_param and hmac.compare_digest(secret_param, secret)) or \
       (secret_header and hmac.compare_digest(secret_header, secret)):
        is_valid = True
    elif github_signature:
        # Read raw request body for HMAC calculation
        body = await request.body()
        # GitHub signature format: sha256=HEX_DIGEST
        if github_signature.startswith("sha256="):
            signature_hash = github_signature.split("sha256=")[1]
            mac = hmac.new(secret.encode(), msg=body, digestmod=hashlib.sha256)
            if hmac.compare_digest(mac.hexdigest(), signature_hash):
                is_valid = True

    if not is_valid:
        logger.warning("Unauthorized deployment trigger attempt.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid deployment secret or signature verification failed"
        )
        
    logger.info("Deployment secret verified. Executing deploy.sh...")
    
    try:
        # Determine path to deploy.sh in the project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        script_path = os.path.join(project_root, "deploy.sh")
        
        # Verify that script exists and is executable
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"deploy.sh not found at {script_path}")
            
        # Spawn deploy.sh in the background
        # We redirect stdout/stderr to files in logs/ directory
        log_dir = os.path.join(project_root, "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # Non-blocking background launch
        subprocess.Popen(
            ["bash", script_path],
            stdout=open(os.path.join(log_dir, "deploy_stdout.log"), "w"),
            stderr=open(os.path.join(log_dir, "deploy_stderr.log"), "w"),
            start_new_session=True  # decouple from the current python process
        )
        return {"status": "Deployment triggered successfully"}
    except Exception as e:
        logger.error(f"Failed to start deployment process: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger deploy.sh: {str(e)}"
        )

