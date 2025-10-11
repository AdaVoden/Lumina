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
        try:
            params = models.AppBskyFeedGetAuthorFeed.Params(actor=did, filter=None, limit=1)
            feed = self.client.app.bsky.feed.get_author_feed(params)

            if feed and feed.feed:
                return feed.feed[0].post.indexed_at
            return None
        except Exception as e:
            logger.debug(f"Error getting last post for {did}: {e}")
            return None
    
    def get_followers(self, did: str, cursor: Optional[str] = None, limit: int = 100):
        """Get followers for a DID with optional cursor for pagination"""
        try:
            params = models.AppBskyGraphGetFollowers.Params( actor = did, 
                                                            cursor=cursor,
                                                             limit = limit )
            return self.client.app.bsky.graph.get_followers(params)
        except Exception as e:
            logger.error(f"Failed to get followers for {did}: {e}")
            raise

    def fetch_all_followers(self, did: str, progress_callback=None) -> list[FollowerData]:
        """Fetch all followers for a DID with progress tracking"""
        all_followers = []
        cursor = None
        processed = 0
         
        while True:
            try:
                # If we can't get the followers there's no work to do
                followers = self.get_followers(did, cursor, config.REPORT_LIMIT)
            except Exception as e:
                logger.error(f"Failed to fetch followers: {e}")
                break

            processed += config.REPORT_LIMIT

            for follower in followers.followers:
                last_posted_at = self.get_last_post(follower.did)
                
                follower_data = FollowerData(
                    did=follower.did,
                    handle=follower.handle,
                    display_name=follower.display_name,
                    last_posted_at=last_posted_at
                )

                all_followers.append(follower_data)

                if progress_callback:
                    progress_callback(processed, len(all_followers))

            if not followers.cursor:
                break

            cursor = followers.cursor
            time.sleep(config.RATE_LIMIT_DELAY)

        return all_followers

def is_active_in_window(last_posted_at: Optional[str], days: int = 31) -> bool:
    """Check if account posted within specified day window"""
    if not last_posted_at:
        return False
    
    posted_at = datetime.fromisoformat(last_posted_at)
    # Date specified number of days in the past
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    return posted_at > cutoff