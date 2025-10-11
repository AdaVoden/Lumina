"""Bluesky  API service layer"""
import logging
import time
from typing import Optional
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, Field

from atproto import IdResolver, Client, models

from config import config

logger = logging.getLogger(__name__)

class FollowerData(BaseModel):
    """Structured Follower data"""
    did: str = Field(..., description="AT Protocol DID")
    handle: str = Field(..., description="AT Protocol user handle")
    display_name: Optional[str] = Field(default=None, description="Display name of user")
    last_posted_at: Optional[str] = Field(default=None, description="Last time user posted")

class ProfileStats(BaseModel):
    """Profile Statistics"""
    did: str = Field(..., description="AT Protocol DID")
    handle: str = Field(..., description="AT Protocol user handle")
    followers_count: int = Field(..., description="Number of followers user has")
    follows_count: int = Field(..., description="Number of follows user has")

class BlueskyService:
    """Service for interacting with Bluesky API"""

    def __init__(self):
        self.client = Client()
        self.resolver = IdResolver()
        self._authenticated = False

    def authenticate(self) -> bool:
        """Authenticate with Bluesky"""
        try:
            self.client.login(login=config.BSKY_HANDLE, password=config.BSKY_APP_PASSWORD)
            self._authenticated = True
            logger.info(f"Authenticated as {config.BSKY_HANDLE}")
            return True
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
        
    def resolve_handle(self, handle: str) -> Optional[str]:
        """Resolve AT protocol handle to a DID"""
        try:
            did = self.resolver.handle.resolve(handle)
            logger.debug(f"Resolved {handle} to {did}")
            return did
        except Exception as e:
            logger.error(f"Failed to resolve handle: {handle}")
            return None

    def get_profile(self, did: str) -> Optional[ProfileStats]:
        """Get profile information for a DID"""
        for attempt in range(config.MAX_RETRIES):
            try:
                params = models.AppBskyActorGetProfile.Params(actor=did)
                profile = self.client.app.bsky.actor.get_profile(params)

                return ProfileStats(
                    handle=profile.handle,
                    did=profile.did,
                    followers_count=profile.followers_count or 0,
                    follows_count=profile.follows_count or 0
                )
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1}/{config.MAX_RETRIES} failed for profile {did}: {e}")
                if attempt < config.MAX_RETRIES - 1:
                    time.sleep(config.RETRY_DELAY)
                else:
                    logger.error(f"Failed to get profile for {did} after {config.MAX_RETRIES} attempts")
                    return None    
            

    def get_last_post(self, did: str) -> Optional[str]:
        """Get the timestamp of the last post for a DID"""
        pass

    def get_followers(self, did: str, cursor: Optional[str] = None, limit: int = 100):
        """Get followers for a DID with optional cursor for pagination"""
        pass

    def fetch_all_followers(self, did: str, progress_callback=None) -> list[FollowerData]:
        """Fetch all followers for a DID with progress tracking"""
        pass

def is_active_in_window(last_posted_at: Optional[str], days: int = 31) -> bool:
    """Check if account posted within specified day window"""
    pass