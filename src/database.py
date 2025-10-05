import sqlite3
import datetime
from datetime import timezone, datetime

DB_PATH = "followers_cache.db"

class Database():

    def _init_tables(self):
        cur = self.cur
        cur.execute("""
        CREATE TABLE IF NOT EXISTS followers (
                    did TEXT PRIMARY KEY,
                    handle TEXT,
                    last_posted_at TEXT,
                    updated_at TEXT
                    )
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

    def get_cached_follower(self, did):
        cur = self.cur
        cur.execute("SELECT last_posted_at, updated_at FROM followers WHERE did = ?", (did,))
        row = cur.fetchone()
        if row:
            return{"last_posted_at": row[0], "updated_at": row[1]}
        return None
    
    def save_follower(self, did, handle, last_posted_at):
        conn = self.conn
        cur = self.cur
        cur.execute("""
            INSERT INTO FOLLOWERS (did, handle, last_posted_at, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(did) DO UPDATE SET
                handle = excluded.handle,
                last_posted_at = excluded.last_posted_at,
                updated_at = excluded.updated_at
            """, (did, handle, last_posted_at, datetime.now(timezone.utc).isoformat(),)
            )
        conn.commit()
