from atproto import IdResolver, Client, models
from math import ceil
from datetime import timedelta, datetime, timezone
from dotenv import load_dotenv
import time
import os

load_dotenv()

HANDLE = os.getenv("BSKY_HANDLE")
APP_PASS = os.getenv("BSKY_APP_PASSWORD")
TARGET_HANDLE = os.getenv("BSKY_TARGET_HANDLE")

REPORT_LIMIT = 25

client = Client()
client.login(login=HANDLE, password=APP_PASS)

def get_profile(did):
    profile = None
    try:
        params = models.AppBskyActorGetProfile.Params(actor=did)
        profile = client.app.bsky.actor.get_profile(params)
    except Exception as e:
        print(f"Encountered error on account: {did}: {e}")
    return profile

def get_last_post(did):
    last_post = None
    try:
        params = models.AppBskyFeedGetAuthorFeed.Params(actor=did, filter=None, limit=1)
        last_post = client.app.bsky.feed.get_author_feed(params)
    except Exception as e:
        print(f"Encountered error on account: {did}: {e}")
    
    return last_post.feed[0].post if (last_post and last_post.feed) else None

def calc_last_month():
    return datetime.now(timezone.utc) - timedelta(days=31)

def posted_in_last_month(post):
    if not post:
        return False
    posted_at = datetime.fromisoformat(post.indexed_at)
    last_month = calc_last_month()
    return posted_at > last_month

def is_account_ghost(post):
    return not post
    
def report(followers, follows, enabled, active, ghost):
    print(f"=========== Report ===========")
    print(f"Followers: {followers}")
    print(f"Follows: {follows}")
    print(f"=========== Followers ===========")
    print(f"Enabled: {enabled}")
    print(f"Disabled: {followers - enabled}")
    print(f"Active: {active}")
    print(f"Active %: {(active/followers)*100:.2f}%")
    print(f"Never Posted: {ghost}")

def main():
    # Resolve DID for future use
    resolver = IdResolver()
    did = resolver.handle.resolve(TARGET_HANDLE)
    profile = get_profile(did)
    if not profile:
        print(f"Could not fetch profile, exiting...")
        return
    print(f"Retreived profile: {profile.handle}")
    # Get followers and go through them all
    try:
        params = models.AppBskyGraphGetFollowers.Params( actor = did, limit = REPORT_LIMIT )
        followers = client.app.bsky.graph.get_followers(params)
    except Exception as e:
        print(f"Failed to get followers for account {profile.handle}: {e}")
    enabled = 0
    active = 0
    ghost = 0
    while True:
        enabled += len(followers.followers)
        for follower in followers.followers:
            # If they posted in the last month they're active
            last_post = get_last_post(follower.did)
            if posted_in_last_month(last_post):
                active += 1
            # If they've never posted it's impossible to tell
            if is_account_ghost(last_post):
                ghost += 1
        if not followers.cursor:
            break
        print(f"Processed {enabled}/{profile.followers_count}...")
        params = models.AppBskyGraphGetFollowers.Params(actor = did, cursor = followers.cursor, limit = 25)
        followers = client.app.bsky.graph.get_followers(params)
        time.sleep(0.05)
    report(profile.followers_count, profile.follows_count, enabled, active, ghost)

if __name__ == "__main__":
    main()
