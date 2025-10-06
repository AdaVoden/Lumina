Now (Core Experience)

    Minimum viable joy — get it working cleanly and reliably.

<details> <summary>Click to expand</summary>

X Login & authenticate via .env

X Fetch profile info (followers/follows)

X Iterate through followers and check activity

X Improve error handling (timeouts, 404s, deleted accounts)

X Add SQLite database for local snapshot storage

    Table: snapshots(date, follower_count, active_followers, total_followers)

    CLI flag: --snapshot to take and save a snapshot

Goal: a simple script that runs once a day and reports current stats.
</details>
Soon (Smarter + More Insightful)

    Moving from “it works” to “it tells me something cool.”

<details> <summary>Click to expand</summary>

Follow/Unfollow tracking between snapshots

Compare DIDs between days

Pretty CLI diff:

    + @newfriend.bsky.social  
    - @ghostaccount.bsky.social

Mutuals detection

    “Show me mutuals only” option

Activity scoring

    Track how many followers are dormant (>90 days no posts)

Simple visualization

Tiny CLI graphs (ASCII bars or sparkline style)

        Optional matplotlib chart output

Goal: actionable insight and personality.
</details>
Later (The Cool Factor)

    Features that make it feel like your own personal dashboard.

<details> <summary>Click to expand</summary>

Manual tagging for accounts (friend, artist, bot, etc.)

Query system:

“Show dormant mutuals”

    “Show artists inactive >30 days”

Local caching of follower data

Automatic daily/weekly snapshots

Minimal Flask web UI (local-only)

Graphs of follower and activity trends

        Interactive filtering

Goal: it feels alive — not just a script but a cozy local tool.
</details>
Maybe / Experimental

    For curiosity or fun
<details> <summary>Click to expand</summary>

Engagement trend prediction (moving averages)

Batch operations (follows/unfollows — carefully)

Hybrid Python + Rust experiments

Data export to CSV/JSON

    “Ghost follower” finder (never interacts)

</details>
Open Source Readiness Checklist

    When these are checked, you can proudly release it.

<details> <summary>Click to expand</summary>

Folder structure: bsky_manager/, main.py, utils/, etc.

.env.example template for others

README.md with setup and usage

requirements.txt with dependencies

Graceful error handling

    Optional fake/demo data for testing

</details>