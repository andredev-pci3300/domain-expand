import sqlite3
import datetime
import os
from contextlib import contextmanager

class CacheManager:
    def __init__(self, db_path="data/history.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize the database with required tables."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Table for tracking processed tweets to avoid duplicates
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS processed_tweets (
                    tweet_id TEXT PRIMARY KEY,
                    account_handle TEXT,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    action_taken TEXT
                )
            ''')
            # Table for tracking daily activity counts
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_activity (
                    date DATE PRIMARY KEY,
                    count INTEGER DEFAULT 0
                )
            ''')
            # Table for metrics history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metrics_history (
                    date DATE PRIMARY KEY,
                    followers INTEGER,
                    following INTEGER,
                    tweets INTEGER,
                    new_followers INTEGER DEFAULT 0,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def log_metrics(self, followers, following, tweets):
        """Logs daily metrics and returns growth since yesterday."""
        today = datetime.date.today().isoformat()
        yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get yesterday's metrics
            cursor.execute('SELECT followers FROM metrics_history WHERE date = ?', (yesterday,))
            result = cursor.fetchone()
            
            prev_followers = result[0] if result else followers
            new_followers = followers - prev_followers
            
            # Insert or Update today's metrics
            # SQLite ON CONFLICT DO UPDATE requires newer version, using REPLACE for simplicity or separate check
            # Better: Upsert syntax
            cursor.execute('''
                INSERT INTO metrics_history (date, followers, following, tweets, new_followers)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(date) DO UPDATE SET
                    followers=excluded.followers,
                    following=excluded.following,
                    tweets=excluded.tweets,
                    new_followers=excluded.new_followers
            ''', (today, followers, following, tweets, new_followers))
            
            conn.commit()
            return new_followers

    def get_todays_report_status(self):
        """Checks if report was already generated today."""
        today = datetime.date.today().isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM metrics_history WHERE date = ?', (today,))
            return cursor.fetchone() is not None

    def is_tweet_processed(self, tweet_id):
        """Check if a tweet has already been processed."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM processed_tweets WHERE tweet_id = ?", (tweet_id,))
            return cursor.fetchone() is not None

    def log_tweet_processed(self, tweet_id, account_handle, action_taken="replied"):
        """Log a tweet as processed."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO processed_tweets (tweet_id, account_handle, action_taken) VALUES (?, ?, ?)",
                (tweet_id, account_handle, action_taken)
            )
            conn.commit()

    def get_daily_count(self):
        """Get the number of actions performed today."""
        today = datetime.date.today().isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT count FROM daily_activity WHERE date = ?", (today,))
            result = cursor.fetchone()
            return result[0] if result else 0

    def increment_daily_count(self):
        """Increment the daily action count."""
        today = datetime.date.today().isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO daily_activity (date, count) VALUES (?, 1)
                ON CONFLICT(date) DO UPDATE SET count = count + 1
            """, (today,))
            conn.commit()
