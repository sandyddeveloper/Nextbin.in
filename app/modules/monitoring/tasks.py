import asyncio
import logging
import socket
import ssl
from datetime import datetime
from urllib.parse import urlparse
import httpx
from sqlalchemy import select
from huey import crontab
from app.workers.huey_app import huey, run_async_safe
from app.modules.monitoring.models import MonitoredProject, PerformanceMetric

logger = logging.getLogger("nextbin.monitoring.tasks")

def get_ssl_expiry_days(url: str) -> int:
    """
    Establish a quick SSL connection to query the certificate details
    and return the remaining lifetime in days.
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme != "https":
            return 999  # HTTP has no SSL expiration
        
        hostname = parsed.hostname
        port = parsed.port or 443
        
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                # e.g., 'May 23 23:59:59 2027 GMT'
                expire_date_str = cert['notAfter']
                expire_date = datetime.strptime(expire_date_str, '%b %d %H:%M:%S %Y %Z')
                remaining = expire_date - datetime.utcnow()
                return max(0, remaining.days)
    except Exception as e:
        logger.warning(f"Failed to fetch SSL certificate details for {url}: {e}")
        return 0

async def ping_single_project(project_id: int):
    """
    Pings a single monitored project, measures latency, checks SSL certificates,
    and commits health state telemetry to SQLite.
    """
    from app.core.database import SessionLocal
    async with SessionLocal() as db:
        result = await db.execute(select(MonitoredProject).where(MonitoredProject.id == project_id))
        project = result.scalar_one_or_none()
        if not project or not project.is_active:
            return

        start_time = datetime.utcnow()
        latency = 0
        status_code = None
        is_up = False
        error_msg = None
        ssl_days = None

        try:
            # Retrieve SSL expiration days remaining
            ssl_days = get_ssl_expiry_days(project.url)
            
            # Fetch target using HTTP client
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(project.url)
                status_code = response.status_code
                latency = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                
                if status_code == project.expected_status_code:
                    is_up = True
                else:
                    error_msg = f"Expected status {project.expected_status_code}, got {status_code}"
        except Exception as e:
            error_msg = str(e)
            latency = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        # Update Project Record
        project.last_status = "UP" if is_up else "DOWN"
        project.last_checked_at = datetime.utcnow()
        project.last_error = error_msg
        
        # Log metric point
        metric = PerformanceMetric(
            project_id=project.id,
            response_time_ms=latency,
            status_code=status_code,
            ssl_days_remaining=ssl_days,
            is_up=is_up,
            error_message=error_msg,
            timestamp=datetime.utcnow()
        )
        db.add(metric)
        await db.commit()
        logger.info(f"Pinged {project.name}: {'UP' if is_up else 'DOWN'} ({latency}ms)")

@huey.task(retries=2, retry_delay=15)
def ping_single_project_task(project_id: int):
    run_async_safe(ping_single_project(project_id))

async def check_all_projects():
    """
    Periodic orchestrator task. Finds all active projects that need ping checks
    and enqueues child tasks to run in parallel.
    """
    from app.core.database import SessionLocal
    async with SessionLocal() as db:
        result = await db.execute(select(MonitoredProject).where(MonitoredProject.is_active == True))
        projects = result.scalars().all()
        
        for project in projects:
            # Trigger checking task per project in background
            ping_single_project_task(project.id)

@huey.periodic_task(crontab(minute="*/1")) # Runs every minute
def check_all_projects_task():
    run_async_safe(check_all_projects())
