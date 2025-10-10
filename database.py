import sqlite3
import datetime
from datetime import timezone, datetime

DB_PATH = "followers_cache.db"

class Database():

    def _init_tables(self):

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    account_handle TEXT,
                    total_followers INTEGER,
                    active_count INTEGER,
                    never_posted_count INTEGER,
                    disabled_count INTEGER
                )                    
        """)

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS snapshot_followers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    snapshot_id INTEGER,
                    did TEXT,
                    handle TEXT,
                    last_posted_at TEXT,
                    display_name TEXT,
                    FOREIGN KEY (snapshot_id) REFERENCES snapshots(id)
                )            
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_snapshot_followers ON snapshot_followers(snapshot_id, did)
        """)

        self.conn.commit()

    def __enter__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cur = self.conn.cursor()
        self._init_tables()
        return self
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        self.conn.commit()
        self.conn.close()

    def create_snapshot(self, account_handle, total_followers, active_count, never_posted_count, disabled_count):
        self.cur.execute("""
                    INSERT INTO snapshots (account_handle, total_followers, active_count, never_posted_count, disabled_count)
                    VALUES (?, ?, ?, ?, ?)
                    """, (account_handle, total_followers, active_count, never_posted_count, disabled_count,)
                    )
        self.conn.commit()
        return self.cur.lastrowid
    
    def get_follower_changes(self, snapshot_id):
        """Compare current snapshot to previous snapshot"""
        cur = self.cur

        cur.execute("""
                    SELECT id FROM snapshots
                    WHERE id < ?
                    ORDER BY id DESC
                    LIMIT 1
                    """, (snapshot_id,))
        
        prev_snapshot = cur.fetchone()
        # If there is no previous snapshot, return nothing
        if not prev_snapshot:
            return {}, {}
        
        prev_id = prev_snapshot[0]

        # Current EXCEPT previous
        cur.execute("""
                    SELECT did, handle FROM snapshot_followers WHERE snapshot_id = ?
                    EXCEPT
                    SELECT did, handle FROM snapshot_followers WHERE snapshot_id = ?
                    """, (snapshot_id, prev_id))
        new_followers = {row[0]: row[1] for row in cur.fetchall()}

        # Previous EXCEPT current
        cur.execute("""
                    SELECT did, handle FROM snapshot_followers WHERE snapshot_id = ?
                    EXCEPT
                    SELECT did, handle FROM snapshot_followers WHERE snapshot_id = ?
                    """, (prev_id, snapshot_id))
        unfollowed = {row[0]: row[1] for row in cur.fetchall()}

        return new_followers, unfollowed

    def add_follower(self, snapshot_id, did, handle, last_posted_at, display_name):
        self.cur.execute("""
            INSERT INTO snapshot_followers (snapshot_id, did, handle, last_posted_at, display_name)
            VALUES (?, ?, ?, ?, ?)
            """, (snapshot_id, did, handle, last_posted_at, display_name,)
            )
        # commit at the _end_ of the snapshot, not per-follower

    def get_last_snapshot(self):
        snapshot = self.get_recent_snapshots(limit=1)
        return snapshot[0]
    
    def get_last_snapshot_id(self):
        self.cur.execute("""
                        SELECT id FROM snapshots
                        ORDER BY timestamp DESC
                        LIMIT 1
                        """)
        return self.cur.fetchone()[0]

        
    def get_recent_snapshots(self, limit=30):
        self.cur.execute("""
                    SELECT id, timestamp, account_handle, total_followers, active_count, never_posted_count, disabled_count
                    FROM snapshots
                    ORDER BY timestamp DESC
                    LIMIT ?
                    """, (limit,))
        rows = self.cur.fetchall()
        return [
            {
                "id": r[0],
                "timestamp": r[1],
                "account_handle": r[2],
                "total_followers": r[3],
                "active_count": r[4],
                "never_posted_count": r[5],
                "disabled_count": r[6],
            }
            for r in rows
        ]

    def get_snapshot_followers(self, snapshot_id, limit=200, offset=0):
        self.cur.execute("""
                        SELECT did, handle, last_posted_at, display_name
                        FROM snapshot_followers
                        WHERE snapshot_id = ?
                        ORDER BY handle COLLATE NOCASE
                        LIMIT ? OFFSET ?
                        """, (snapshot_id, limit, offset))
        rows = self.cur.fetchall()
        return [
            {"did": r[0], "handle": r[1], "last_posted_at": r[2], "display_name": r[3]}
            for r in rows
        ]

    def get_snapshot_series(self, limit=100):
        """Return chronological series for charing: oldest->newest."""
        self.cur.execute("""
            SELECT 
                         strftime('%Y-%m-%d', timestamp) as date, 
                         total_followers, 
                         active_count
            FROM snapshots
            ORDER BY timestamp ASC
            LIMIT ?                 
        """, (limit,))
        rows = self.cur.fetchall()
        return [{"timestamp": r[0], "total_followers": r[1], "active_count": r[2]} for r in rows]