import logging
from typing import Optional

from database import Database
from bluesky_service import FollowerData, ProfileStats
from analytics import FollowerStats, SnapshotReport

logger = logging.getLogger(__name__)

class SnapshotService:
    """Service for creating and managing follower snapshots"""

    def __init__(self, db: Database):
        self.db = db

    def create_snapshot(
            self,
            profile: ProfileStats,
            followers: list[FollowerData],
            stats: FollowerStats
    ) -> Optional[int]:
        """Create a new snapshot with follower data"""
        with self.db as db:
            try:
                snapshot_id = db.create_snapshot(
                    account_handle=profile.handle,
                    total_followers=profile.followers_count,
                    active_count=stats.active_count,
                    never_posted_count=stats.ghost_count,
                    disabled_count=stats.disabled_count
                )

                logger.info(f"Created snapshot {snapshot_id} for {profile.handle}")

                # Add in batches for better error recovery
                batch_size = 100
                for i in range(0, len(followers), batch_size):
                    batch = followers[i:i + batch_size]

                    for follower in batch:
                        db.add_follower(
                            snapshot_id=snapshot_id,
                            did=follower.did,
                            handle=follower.handle,
                            last_posted_at=follower.last_posted_at,
                            display_name=follower.display_name
                        )
                    
                    # commit each batch
                    db.conn.commit()
                    logger.debug(f"Committed batch {i // batch_size + 1} ({len(batch)} followers)")

                logger.info(f"Saved {len(followers)} followers to snapshot {snapshot_id}")
                return snapshot_id

            except Exception as e:
                logger.error(f"Failed to create snapshot: {e}")
                self.db.conn.rollback()
                return None

    def generate_report(
            self,
            snapshot_id: int,
            stats: FollowerStats,
            follows_count: int
    ) -> Optional[SnapshotReport]:
        """Generate a report comparing this snapshot to the previous one"""
        with self.db as db:
            try:
                new_followers, unfollows = db.get_follower_changes(snapshot_id)

                return SnapshotReport(
                    stats=stats,
                    new_followers=new_followers,
                    unfollowers=unfollows,
                    follows_count=follows_count
                )
            except Exception as e:
                logger.error(f"Failed to generate report: {e}")
                return None