import json
import logging
from typing import Optional, Dict, Any
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired, FeedbackRequired
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.security import decrypt_credential
from app.core.database import SessionLocal
from app.modules.instagram.models import InstagramAccount

logger = logging.getLogger("nextbin.instagram")

class InstagramClientManager:
    """
    Manager for instagrapi Client connections.
    Caches and reuses sessions, storing them securely in SQLite to bypass login security challenges.
    """
    
    def __init__(self):
        self._clients: Dict[str, Client] = {}

    def _get_configured_client(self) -> Client:
        cl = Client()
        # Set a healthy random delay between API calls to prevent bot detection rate limits
        cl.delay_range = [1, 3]
        return cl

    async def get_client(self, db: AsyncSession, account_id: int) -> Client:
        """
        Retrieves a logged-in instagrapi Client for a given account ID.
        Attempts session restoration from database before falling back to full login credentials.
        """
        # Load account from DB
        result = await db.execute(select(InstagramAccount).where(InstagramAccount.id == account_id))
        account = result.scalar_one_or_none()
        if not account:
            raise ValueError(f"Instagram Account {account_id} not found in database.")

        # Check if already cached in RAM
        if account.username in self._clients:
            try:
                # Fast check if session is still alive
                self._clients[account.username].get_timeline_feed()
                return self._clients[account.username]
            except Exception:
                logger.info(f"Cached client for {account.username} expired. Re-authenticating...")
                self._clients.pop(account.username)

        cl = self._get_configured_client()

        # Step 1: Try session cookies restoration
        if account.session_settings:
            try:
                settings_dict = json.loads(account.session_settings)
                cl.set_settings(settings_dict)
                # Test login validation
                cl.login_by_sessionid(settings_dict["uuids"]["phone_id"]) # dummy check or trigger check
                # Verify session integrity
                cl.get_timeline_feed()
                logger.info(f"Successfully restored Instagram session for {account.username} from DB")
                self._clients[account.username] = cl
                account.status = "CONNECTED"
                await db.commit()
                return cl
            except (LoginRequired, Exception) as e:
                logger.warning(f"Session restoration failed for {account.username}: {e}. Falling back to password login.")

        # Step 2: Fallback to full Username / Password Login
        password = decrypt_credential(account.encrypted_password)
        try:
            logger.info(f"Attempting fresh login for Instagram user: {account.username}")
            cl.login(account.username, password)
            
            # Serialize and save session settings back to DB
            session_settings = cl.get_settings()
            account.session_settings = json.dumps(session_settings)
            account.status = "CONNECTED"
            await db.commit()
            
            self._clients[account.username] = cl
            return cl
        except ChallengeRequired as cre:
            logger.error(f"Instagram login challenge required for {account.username}: {cre}")
            account.status = "2FA_REQUIRED"
            await db.commit()
            raise
        except FeedbackRequired as fre:
            logger.error(f"Instagram rate limits or feedback block for {account.username}: {fre}")
            account.status = "ERROR"
            await db.commit()
            raise
        except Exception as e:
            logger.error(f"Failed login for {account.username}: {e}")
            account.status = "ERROR"
            await db.commit()
            raise

instagram_manager = InstagramClientManager()
