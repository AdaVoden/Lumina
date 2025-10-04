from atproto import IdResolver, Client, models
from math import ceil
from datetime import timedelta, datetime, timezone
from dotenv import load_dotenv
import os

load_dotenv()

HANDLE = os.getenv("BSKY_HANDLE")
APP_PASS = os.getenv("BSKY_APP_PASSWORD")
REPORT_LIMIT = 25
TARGET_HANDLE = ""


client = Client()
client.login(login=HANDLE, password=APP_PASS)

def get_profile(did):
    params = models.AppBskyActorGetProfile.Params(actor=did)
    profile = client.app.bsky.actor.get_profile(params)
    return profile

def calc_last_month():
    return datetime.now(timezone.utc) - timedelta(days=31)

def posted_in_last_month(did):

    params = models.AppBskyFeedGetAuthorFeed.Params(actor=did, filter=None,limit=1)
    last_post = client.app.bsky.feed.get_author_feed(params)
    if len(last_post.feed) > 0:
        posted_at = datetime.fromisoformat(last_post.feed[0].post.indexed_at)
    else:
        # No data to work from
        return False
    last_month = calc_last_month()
    return posted_at > last_month


# def liked_in_last_month(did):
#     # Doesn't work, needs direct user authentication
#     params = models.AppBskyFeedGetActorLikes.Params(actor=did, limit=1)
#     last_like = client.app.bsky.feed.get_actor_likes(params)
#     posted_at = datetime.fromtimestamp(last_like.feed[0].post.indexed_at)
#     last_month = calc_last_month()
#     return posted_at > last_month


def is_account_active(did):
    return posted_in_last_month(did)

def main():
    # Resolve DID for future use
    resolver = IdResolver()
    did = resolver.handle.resolve(TARGET_HANDLE)
    profile = get_profile(did)
    print(did)
    print (f"Raw number of followers: {profile.followers_count}")
    print (f"Raw number of follows: {profile.follows_count}")

    # Get followers and go through them all
    params = models.AppBskyGraphGetFollowers.Params( actor = did, limit = REPORT_LIMIT )
    followers = client.app.bsky.graph.get_followers(params)
    enabled = 0
    active = 0
    for _ in range(ceil(profile.followers_count / REPORT_LIMIT)):
        enabled += len(followers.followers)
        for follower in followers.followers:
            if is_account_active(follower.did):
                active += 1
        params = models.AppBskyGraphGetFollowers.Params(actor = did, cursor = followers.cursor, limit = 25)
        followers = client.app.bsky.graph.get_followers(params)
    print(f"Number of enabled followers: {enabled}")
    print(f"Number of disabled accounts: {profile.followers_count - enabled}")
    print(f"Number of active accounts: {active}")

if __name__ == "__main__":
    main()
