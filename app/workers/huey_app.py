import os
import asyncio
from huey import SqliteHuey
from app.core.config import settings

# Enforce existence of queue file directory
os.makedirs(os.path.dirname(settings.QUEUE_DB_PATH), exist_ok=True)

# Initialize SqliteHuey. The file stores tasks, schedules, and results.
huey = SqliteHuey(
    filename=settings.QUEUE_DB_PATH,
    fsync=True,  # Ensures data is flushed to disk for maximum crash durability
)

def run_async_safe(coro):
    """
    Safely execute an async coroutine from a synchronous worker context.
    Detects running event loops (common in pytest/FastAPI) and schedules
    the task on the active loop instead of calling asyncio.run() to avoid crashes.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        return loop.create_task(coro)
    else:
        return asyncio.run(coro)
