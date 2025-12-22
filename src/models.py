"""Data models for the news brief system."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class Source:
    """Represents a news source (RSS feed)."""
    id: str
    name: str
    rss_url: str
    tier: str  # wire, news, magazine
    region: str


@dataclass
class NewsItem:
    """Represents a single news article/item from RSS."""
    id: Optional[int]
    source_id: str
    title: str
    link: str
    published_at: datetime
    summary: Optional[str]
    fetched_at: datetime
    guid_hash: str

    def __post_init__(self):
        """Ensure datetime objects are properly typed."""
        if isinstance(self.published_at, str):
            from dateutil import parser
            self.published_at = parser.parse(self.published_at)
        if isinstance(self.fetched_at, str):
            from dateutil import parser
            self.fetched_at = parser.parse(self.fetched_at)


@dataclass
class Event:
    """Represents a clustered news event (multiple articles about same story)."""
    id: Optional[int]
    items: List[NewsItem]
    created_at: datetime
    score: float = 0.0
    canonical_title: str = ""

    def __post_init__(self):
        """Initialize computed fields."""
        if not self.canonical_title and self.items:
            # Use shortest title as canonical (often clearer)
            self.canonical_title = min(
                (item.title for item in self.items),
                key=len
            )

    @property
    def source_count(self) -> int:
        """Number of distinct sources reporting this event."""
        return len(set(item.source_id for item in self.items))

    @property
    def source_ids(self) -> List[str]:
        """List of distinct source IDs."""
        return list(set(item.source_id for item in self.items))

    @property
    def most_recent_time(self) -> datetime:
        """Most recent publication time among all items."""
        return max(item.published_at for item in self.items)
