import asyncio
import logging
from app.core.logging import setup_logging
from app.workers.huey_app import huey, run_async_safe
from app.core.database import engine
from app.models import Base

# Initialize custom Worker rotating logger
setup_logging("worker")
logger = logging.getLogger("nextbin.worker")

# Ensure database tables exist for the worker processes
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

try:
    logger.info("Initializing database tables for background worker...")
    run_async_safe(init_db())
    logger.info("Database tables initialized successfully for background worker.")
except Exception as e:
    logger.error(f"Error initializing database for background worker: {e}")

@huey.task()
def test_connection_task(payload: str) -> str:
    """
    Simple verification task to confirm the worker is executing tasks.
    """
    logger.info(f"Executing test connection task with payload: {payload}")
    print(f"[WORKER TEST] Received payload: {payload}")
    return f"Processed: {payload}"

# Module-specific tasks will be imported here to register them with the consumer:
try:
    from app.modules.monitoring.tasks import check_all_projects_task
    from app.modules.instagram.tasks import poll_instagram_messages_task, connect_instagram_account_task
    from app.modules.blog.tasks import sync_blog_content_task
except ImportError as e:
    logger.warning(f"Some modules could not be imported yet: {e}")
