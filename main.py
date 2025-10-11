import logging
from atproto import IdResolver, Client, models
from datetime import timedelta, datetime, timezone
import time
import os
from database import Database
from config import config

logger = logging.getLogger(__name__)


def main():
    with Database() as db:

        # Create out snapshot
        snapshot_id = db.create_snapshot(account_handle=profile.handle,
                                            total_followers=profile.followers_count,
                                            active_count=active,
                                            never_posted_count=ghost,
                                            disabled_count=disabled)
        print(f"Saving snapshot {snapshot_id} with {len(follower_data)} followers...")

        # Add all followers to this snapshot
        for follower in follower_data:
            db.add_follower(snapshot_id=snapshot_id,
                            did=follower.did,
                            handle=follower.handle,
                            last_posted_at=follower.last_posted_at,
                            display_name=follower.display_name)
            
        db.conn.commit()
        print(f"Snapshot saved!")

        new_followers, unfollows = db.get_follower_changes(snapshot_id)
        report(profile.followers_count, profile.follows_count, enabled, active, ghost, new_followers, unfollows)

if __name__ == "__main__":
    main()
