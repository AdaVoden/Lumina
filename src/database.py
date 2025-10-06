import sqlite3
import datetime
from datetime import timezone, datetime

DB_PATH = "followers_cache.db"

class Database():

    def _init_tables(self):
        cur = self.cur

        cur.execute("""
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

        cur.execute("""
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

        cur.execute("""
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
        cur = self.cur
        cur.execute("""
                    INSERT INTO snapshots (account_handle, total_followers, active_count, never_posted_count, disabled_count)
                    VALUES (?, ?, ?, ?, ?)
                    """, (account_handle, total_followers, active_count, never_posted_count, disabled_count,)
                    )
        self.conn.commit()
        return cur.lastrowid
    
    def get_follower_changes(db, snapshot_id):
        """Compare current snapshot to previous snapshot"""
        cur = db.cur

        # GEt current snapshot
        cur.execute("""
                    SELECT did, handle, last_posted_at FROM snapshot_followers
                    WHERE snapshot_id = ?
                    """, (snapshot_id,))
        current = {row[0]: {'handle': row[1], 'last_posted_at': row[2]} for row in cur.fetchall()}
        
        # Get previous snapshot
        cur.execute("""
                    SELECT did, handle, last_posted_at FROM snapshot_followers
                    WHERE snapshot_id = (
                        SELECT id FROM snapshots
                        WHERE id < ?
                        ORDER BY id DESC
                        LIMIT 1
                    )
                    """, (snapshot_id,))
        prev = cur.fetchone()
        
        if not prev:
            # First snapshot, everyone is new!
            return list(current.keys()), []
        
        prev = {row[0]: {'handle': row[1], 'last_posted_at': row[2]} for row in cur.fetchall()}

        new_followers = {did: current[did]['handle'] for did in current if did not in prev}
        unfollowed = {did: prev[did]['handle'] for did in prev if did not in current}

    # def get_cached_follower(self, did):
    #     cur = self.cur
    #     cur.execute("SELECT last_posted_at, updated_at FROM followers WHERE did = ?", (did,))
    #     row = cur.fetchone()
    #     if row:
    #         return{"last_posted_at": row[0], "updated_at": row[1]}
    #     return None
    
    def add_follower(self, snapshot_id, did, handle, last_posted_at, display_name):
        cur = self.cur

        cur.execute("""
            INSERT INTO snapshot_followers (snapshot_id, did, handle, last_posted_at, display_name)
            VALUES (?, ?, ?, ?, ?)
            """, (snapshot_id, did, handle, last_posted_at, display_name,)
            )
        
        # commit at the _end_ of the snapshot, not per-follower
