import asyncio
import logging
from datetime import datetime
from sqlalchemy import select
from huey import crontab
from app.workers.huey_app import huey, run_async_safe
from app.modules.instagram.models import InstagramAccount, InstagramChatLog, InstagramRule
from app.modules.instagram.client import instagram_manager

logger = logging.getLogger("nextbin.instagram.tasks")

@huey.task(retries=3, retry_delay=30, backoff=2)
def send_instagram_message_task(account_id: int, thread_id: str, text: str):
    """
    Background worker task to send a Direct Message to a specific Instagram thread.
    Retries automatically with exponential backoff if the network fails.
    """
    async def _execute():
        from app.core.database import SessionLocal
        async with SessionLocal() as db:
            cl = await instagram_manager.get_client(db, account_id)
            # Send message via instagrapi
            cl.direct_send(text, thread_ids=[thread_id])
            logger.info(f"Successfully sent DM to thread {thread_id} for account {account_id}")
            
    run_async_safe(_execute())

@huey.task(retries=2, retry_delay=15)
def connect_instagram_account_task(account_id: int):
    """
    Background worker task to trigger an initial login session for an Instagram account,
    which serializes the cookies to SQLite and sets status to CONNECTED.
    """
    async def _execute():
        from app.core.database import SessionLocal
        async with SessionLocal() as db:
            logger.info(f"Triggering background connection for Instagram Account ID: {account_id}")
            # get_client automatically handles login and status updates in DB
            cl = await instagram_manager.get_client(db, account_id)
            logger.info(f"Instagram Account {cl.username} (ID: {account_id}) connected successfully!")
            
    run_async_safe(_execute())

@huey.periodic_task(crontab(minute="*/5")) # Run every 5 minutes
def poll_instagram_messages_task():
    """
    Periodic task to scan unread messages, check them against response rules,
    send auto-replies, and log conversation history.
    """
    async def _execute():
        from app.core.database import SessionLocal
        async with SessionLocal() as db:
            # Query all active connected or newly linked accounts
            result = await db.execute(
                select(InstagramAccount).where(
                    InstagramAccount.is_active == True,
                    InstagramAccount.status.in_(["CONNECTED", "DISCONNECTED"])
                )
            )
            accounts = result.scalars().all()
            
            for account in accounts:
                try:
                    cl = await instagram_manager.get_client(db, account.id)
                    
                    # Fetch active auto-reply rules for the account
                    rules_result = await db.execute(
                        select(InstagramRule).where(
                            InstagramRule.account_id == account.id,
                            InstagramRule.is_active == True
                        )
                    )
                    rules = rules_result.scalars().all()
                    if not rules:
                        continue
                    
                    # Fetch unread threads/messages
                    threads = cl.direct_threads(amount=10, selected_filter="unread")
                    for thread in threads:
                        # Fetch messages in this thread
                        for msg in thread.messages:
                            # Skip if this message is sent by us
                            if msg.user_id == cl.user_id:
                                continue
                            
                            # Verify if we already processed this message
                            log_check = await db.execute(
                                select(InstagramChatLog).where(InstagramChatLog.message_id == str(msg.id))
                            )
                            if log_check.scalar_one_or_none():
                                continue # Already replied
                            
                            # Check text for triggers
                            msg_text = (msg.text or "").strip().lower()
                            reply_text = None
                            for rule in rules:
                                if rule.trigger_keyword.lower() in msg_text:
                                    reply_text = rule.response_text
                                    break
                            
                            # Store message log
                            chat_log = InstagramChatLog(
                                account_id=account.id,
                                thread_id=thread.id,
                                message_id=str(msg.id),
                                sender_username=msg.username or "unknown",
                                text=msg.text,
                                direction="INCOMING",
                                timestamp=msg.timestamp or datetime.utcnow()
                            )
                            db.add(chat_log)
                            
                            # If a rule was triggered, send auto-reply
                            if reply_text:
                                logger.info(f"Auto-reply triggered for keyword. Sending response to thread: {thread.id}")
                                # Send reply (can call client synchronously here inside loop or trigger subtask)
                                cl.direct_send(reply_text, thread_ids=[thread.id])
                                
                                # Store outgoing log
                                reply_log = InstagramChatLog(
                                    account_id=account.id,
                                    thread_id=thread.id,
                                    message_id=f"reply_{msg.id}",
                                    sender_username=cl.username,
                                    text=reply_text,
                                    direction="OUTGOING",
                                    timestamp=datetime.utcnow()
                                )
                                db.add(reply_log)
                                
                    account.last_synced_at = datetime.utcnow()
                    await db.commit()
                except Exception as e:
                    logger.error(f"Error polling messages for Instagram account {account.username}: {e}")
                    
    run_async_safe(_execute())
