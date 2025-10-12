# Lumina - Bluesky Follower Tracker

A Python tool for tracking and analyzing your Bluesky followers over time. Monitor follower activity, track new followers and unfollows, and visualize follower trends through a web interface.

## Features

- **Follower Analytics** - Track active vs. inactive followers
- **Historical Snapshots** - Compare follower changes over time
- **Activity Monitoring** - Identify accounts that haven't posted recently
- **Web Interface** - View your follower data and trends in a browser
- **Local Storage** - All data stored in a local SQLite database
- **Multi-Account Support** - Track multiple Bluesky accounts

## Prerequisites

- Python 3.8 or higher
- A Bluesky account
- A Bluesky App Password (see Configuration section)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/MorriganDeSade/Lumina.git
   cd lumina
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. **Create a `.env` file** in the project root:
   ```bash
   cp .env.example .env  # Or create manually
   ```

2. **Add your Bluesky credentials** to `.env`:
   ```env
   BSKY_HANDLE=your-handle.bsky.social
   BSKY_APP_PASSWORD=your-app-password-here
   BSKY_TARGET_HANDLE=account-to-track.bsky.social
   ```

### Getting a Bluesky App Password

**Important:** Do NOT use your regular Bluesky password!

1. Log in to Bluesky (web or app)
2. Go to Settings → Privacy and Security → App Passwords
3. Click "Add App Password"
4. Give it a name (e.g., "Follower Tracker")
5. Copy the generated password and paste it into your `.env` file

### Configuration Options

You can customize these settings in `.env` (all optional):

```env
# API Settings
REPORT_LIMIT=100              # Followers fetched per API request (1-100)
RATE_LIMIT_DELAY=0.05        # Delay between requests in seconds
MAX_RETRIES=3                # Number of retry attempts for failed requests
RETRY_DELAY=1.0              # Delay between retries in seconds

# Activity Settings
ACTIVITY_WINDOW_DAYS=31      # Days to consider a user "active"
```

## Usage

### Taking a Snapshot

Run the tracker to capture a snapshot of your followers:

```bash
python main.py
```

This will:
- Fetch all followers for the target account
- Check each follower's last post date
- Calculate activity statistics
- Store the snapshot in the database
- Display a report showing changes since the last snapshot

**Example output:**
```
==================================================
FOLLOWER REPORT
==================================================

Total Followers: 1,234
Follows: 567

==================================================
FOLLOWER BREAKDOWN
==================================================
Enabled Accounts: 1,200
Disabled Accounts: 34
Active (posted in last 31 days): 856
Active Percentage: 69.39%
Never Posted: 89

==================================================
NEW FOLLOWERS (12)
==================================================
  + alice.bsky.social
  + bob.example.com
  ...
```

### Viewing Data in the Web Interface

1. **Start the web server:**
   ```bash
   python web.py
   ```

2. **Open your browser** to `http://localhost:5000`

The web interface shows:
- Recent snapshots with statistics
- Follower trends over time (chart)
- Detailed follower lists for each snapshot
- Activity breakdowns

## How It Works

The tracker analyzes your Bluesky followers by:

1. **Fetching followers** - Gets all accounts following the target handle
2. **Checking activity** - Looks at each follower's last post date
3. **Categorizing accounts**:
   - **Active** - Posted within the last 31 days (configurable)
   - **Inactive** - Haven't posted recently but have posted before
   - **Ghost** - Never made a post
   - **Disabled** - Account deleted or suspended

4. **Tracking changes** - Compares to previous snapshots to identify:
   - New followers
   - Unfollows
   - Activity changes over time

All data is stored locally in `followers_cache.db` and never leaves your machine.

## Project Structure

```
bluesky-follower-tracker/
├── main.py                  # CLI entry point for taking snapshots
├── web.py                   # Web interface server
├── config.py                # Configuration management
├── database.py              # Database operations
├── bluesky_service.py       # Bluesky API client
├── analytics.py             # Statistics and reporting
├── snapshot_service.py      # Snapshot management
├── requirements.txt         # Python dependencies
├── .env                     # Your configuration (create this)
└── followers_cache.db       # SQLite database (created automatically)
```

## Performance

- Processes approximately **11 followers per second**
- For an account with 1,000 followers, expect ~90 seconds per snapshot
- Rate limiting is built-in to respect Bluesky's API

## Troubleshooting

### "Authentication failed"
- Make sure you're using an **App Password**, not your regular password
- Check that your handle includes the full domain (e.g., `user.bsky.social`)

### "Could not resolve handle"
- Verify the target handle is spelled correctly
- Make sure the account exists and is not suspended

### "No module named 'pydantic'"
- Run `pip install -r requirements.txt` to install all dependencies

### Web interface won't start
- Make sure port 5000 is not in use
- Check that Flask is installed: `pip install flask`

## Privacy & Security

- All data is stored **locally** on your machine
- Your App Password is stored in `.env` (add `.env` to `.gitignore`!)
- No data is sent to any third-party services
- The tool only reads public Bluesky data

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

MIT

## Acknowledgments

Built with:
- [atproto](https://github.com/MarshalX/atproto) - Python SDK for AT Protocol/Bluesky
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [Flask](https://flask.palletsprojects.com/) - Web framework

---

**Note:** This is an unofficial tool and is not affiliated with Bluesky Social PBC.
