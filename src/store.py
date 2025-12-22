"""Database storage and retrieval for news items and events."""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any

from .models import Source, NewsItem, Event
from .utils import get_data_path


class NewsDatabase:
    """SQLite database for storing news items and events."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize database connection."""
        if db_path is None:
            db_path = get_data_path('news.db')

        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None

    def connect(self) -> None:
        """Connect to the database and create tables if needed."""
        # Ensure data directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()

        # Sources table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sources (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                rss_url TEXT NOT NULL,
                tier TEXT NOT NULL,
                region TEXT NOT NULL
            )
        ''')

        # Items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT NOT NULL,
                title TEXT NOT NULL,
                link TEXT NOT NULL,
                published_at TEXT NOT NULL,
                summary TEXT,
                fetched_at TEXT NOT NULL,
                guid_hash TEXT UNIQUE NOT NULL,
                FOREIGN KEY (source_id) REFERENCES sources(id)
            )
        ''')

        # Events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                score REAL DEFAULT 0.0,
                canonical_title TEXT
            )
        ''')

        # Event-Item junction table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_items (
                event_id INTEGER NOT NULL,
                item_id INTEGER NOT NULL,
                PRIMARY KEY (event_id, item_id),
                FOREIGN KEY (event_id) REFERENCES events(id),
                FOREIGN KEY (item_id) REFERENCES items(id)
            )
        ''')

        # Create indices for common queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_items_published
            ON items(published_at)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_items_source
            ON items(source_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_items_guid
            ON items(guid_hash)
        ''')

        self.conn.commit()

    def upsert_source(self, source: Source) -> None:
        """Insert or update a source."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO sources (id, name, rss_url, tier, region)
            VALUES (?, ?, ?, ?, ?)
        ''', (source.id, source.name, source.rss_url, source.tier, source.region))
        self.conn.commit()

    def get_source(self, source_id: str) -> Optional[Source]:
        """Retrieve a source by ID."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM sources WHERE id = ?', (source_id,))
        row = cursor.fetchone()

        if row:
            return Source(
                id=row['id'],
                name=row['name'],
                rss_url=row['rss_url'],
                tier=row['tier'],
                region=row['region']
            )
        return None

    def insert_item(self, item: NewsItem) -> Optional[int]:
        """
        Insert a news item into the database.

        Returns the item ID if inserted, None if duplicate.
        """
        cursor = self.conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO items
                (source_id, title, link, published_at, summary, fetched_at, guid_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                item.source_id,
                item.title,
                item.link,
                item.published_at.isoformat(),
                item.summary,
                item.fetched_at.isoformat(),
                item.guid_hash
            ))
            self.conn.commit()
            return cursor.lastrowid

        except sqlite3.IntegrityError:
            # Duplicate guid_hash
            return None

    def get_recent_items(self, hours: int = 24) -> List[NewsItem]:
        """
        Retrieve items published within the last N hours.

        Args:
            hours: Number of hours to look back

        Returns:
            List of NewsItem objects
        """
        cursor = self.conn.cursor()

        # Calculate cutoff time
        from datetime import timedelta
        # Use replace to make timezone-naive for database comparison
        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=hours)

        cursor.execute('''
            SELECT * FROM items
            WHERE published_at >= ?
            ORDER BY published_at DESC
        ''', (cutoff.isoformat(),))

        items = []
        for row in cursor.fetchall():
            items.append(NewsItem(
                id=row['id'],
                source_id=row['source_id'],
                title=row['title'],
                link=row['link'],
                published_at=row['published_at'],
                summary=row['summary'],
                fetched_at=row['fetched_at'],
                guid_hash=row['guid_hash']
            ))

        return items

    def create_event(self, item_ids: List[int], score: float = 0.0,
                    canonical_title: str = "") -> int:
        """
        Create a new event and associate items with it.

        Returns the event ID.
        """
        cursor = self.conn.cursor()

        # Create event
        cursor.execute('''
            INSERT INTO events (created_at, score, canonical_title)
            VALUES (?, ?, ?)
        ''', (datetime.now(timezone.utc).replace(tzinfo=None).isoformat(), score, canonical_title))

        event_id = cursor.lastrowid

        # Associate items
        for item_id in item_ids:
            cursor.execute('''
                INSERT INTO event_items (event_id, item_id)
                VALUES (?, ?)
            ''', (event_id, item_id))

        self.conn.commit()
        return event_id

    def get_event(self, event_id: int) -> Optional[Event]:
        """Retrieve an event with all its items."""
        cursor = self.conn.cursor()

        # Get event metadata
        cursor.execute('SELECT * FROM events WHERE id = ?', (event_id,))
        event_row = cursor.fetchone()

        if not event_row:
            return None

        # Get associated items
        cursor.execute('''
            SELECT i.* FROM items i
            JOIN event_items ei ON i.id = ei.item_id
            WHERE ei.event_id = ?
        ''', (event_id,))

        items = []
        for row in cursor.fetchall():
            items.append(NewsItem(
                id=row['id'],
                source_id=row['source_id'],
                title=row['title'],
                link=row['link'],
                published_at=row['published_at'],
                summary=row['summary'],
                fetched_at=row['fetched_at'],
                guid_hash=row['guid_hash']
            ))

        return Event(
            id=event_row['id'],
            items=items,
            created_at=event_row['created_at'],
            score=event_row['score'],
            canonical_title=event_row['canonical_title']
        )

    def get_recent_events(self, limit: Optional[int] = None) -> List[Event]:
        """
        Retrieve recent events ordered by score.

        Args:
            limit: Maximum number of events to return

        Returns:
            List of Event objects
        """
        cursor = self.conn.cursor()

        query = 'SELECT id FROM events ORDER BY score DESC, created_at DESC'
        if limit:
            query += f' LIMIT {limit}'

        cursor.execute(query)

        events = []
        for row in cursor.fetchall():
            event = self.get_event(row['id'])
            if event:
                events.append(event)

        return events

    def clear_old_events(self, keep_days: int = 7) -> None:
        """
        Delete events older than specified days.

        Args:
            keep_days: Number of days of events to keep
        """
        cursor = self.conn.cursor()

        from datetime import timedelta
        # Use replace to make timezone-naive for database comparison
        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=keep_days)

        # Delete old event-item associations
        cursor.execute('''
            DELETE FROM event_items
            WHERE event_id IN (
                SELECT id FROM events WHERE created_at < ?
            )
        ''', (cutoff.isoformat(),))

        # Delete old events
        cursor.execute('''
            DELETE FROM events WHERE created_at < ?
        ''', (cutoff.isoformat(),))

        self.conn.commit()
