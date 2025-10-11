import logging
import sys
from tqdm import tqdm

from database import Database
from config import config
from bluesky_service import BlueskyService
from analytics import AnalyticsService
from snapshot_service import SnapshotService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('follower_tracker.log')
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main execution function"""

    bluesky = BlueskyService()

    if not bluesky.authenticate():
        logger.error("Failed to authenticate with Bluesky")
        sys.exit(1)

    # resolve target account
    logger.info(f"Resolving handle: {config.BSKY_TARGET_HANDLE}")
    target_did = bluesky.resolve_handle(config.BSKY_TARGET_HANDLE)

    if not target_did:
        logger.error(f"Could not resolve handle: {config.BSKY_TARGET_HANDLE}")
        sys.exit(1)

    # Get profile of target
    logger.info("Fetching profile information")
    profile = bluesky.get_profile(target_did)

    if not profile:
        logger.error(f"Could not fetch profile: {config.BSKY_TARGET_HANDLE}")
        sys.exit(1)

    logger.info(f"Tracking followers for: {profile.handle} ({profile.followers_count} followers)")

    # Fetch all followers with a progress bar
    print(f"\nFetching followers for {profile.handle}...")
    pbar = tqdm(total=profile.followers_count, desc="Processing followers", unit="followers")

    def progress_callback(processed, fetched):
        pbar.n = fetched
        pbar.refresh()

    followers = bluesky.fetch_all_followers(target_did, progress_callback)
    pbar.close()

    logger.info(f"Fetched {len(followers)} followers")

    # Calculate statistics
    logger.info("Calculating statistics")
    stats = AnalyticsService.calculate_stats(profile.followers_count, followers)

    with Database() as db:
        snapshot_service = SnapshotService(db)

        logger.info("Creating snapshot")
        snapshot_id = snapshot_service.create_snapshot(profile, followers, stats)

        if not snapshot_id:
            logger.error("Failed to create snapshot")
            sys.exit(1)

        # Generate and display report
        logger.info("Generating report")
        report = snapshot_service.generate_report(
            snapshot_id,
            stats,
            profile.follows_count
        )

        if report:
            print("\n")
            AnalyticsService.print_report(report)
        else:
            logger.error("Failed to generate report")
            sys.exit(1)

    logger.info("Follower tracking complete")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)
