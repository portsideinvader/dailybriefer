"""Tests for data models."""

import pytest
from datetime import datetime
from src.models import Source, NewsItem, Event


class TestSource:
    """Test Source model."""

    def test_source_creation(self):
        """Test creating a Source."""
        source = Source(
            id="test_source",
            name="Test Source",
            rss_url="https://example.com/rss",
            tier="news",
            region="US"
        )

        assert source.id == "test_source"
        assert source.name == "Test Source"
        assert source.tier == "news"
        assert source.region == "US"


class TestNewsItem:
    """Test NewsItem model."""

    def test_news_item_creation(self):
        """Test creating a NewsItem."""
        now = datetime.utcnow()

        item = NewsItem(
            id=1,
            source_id="test_source",
            title="Test Article",
            link="https://example.com/article",
            published_at=now,
            summary="Test summary",
            fetched_at=now,
            guid_hash="abc123"
        )

        assert item.id == 1
        assert item.title == "Test Article"
        assert item.source_id == "test_source"


class TestEvent:
    """Test Event model."""

    def test_event_source_count(self):
        """Test that source_count returns distinct source count."""
        now = datetime.utcnow()

        items = [
            NewsItem(1, "source1", "Title1", "http://link1", now, None, now, "hash1"),
            NewsItem(2, "source1", "Title2", "http://link2", now, None, now, "hash2"),
            NewsItem(3, "source2", "Title3", "http://link3", now, None, now, "hash3"),
            NewsItem(4, "source3", "Title4", "http://link4", now, None, now, "hash4"),
        ]

        event = Event(id=1, items=items, created_at=now)

        # Should have 3 distinct sources: source1, source2, source3
        assert event.source_count == 3

    def test_event_source_ids(self):
        """Test that source_ids returns unique source IDs."""
        now = datetime.utcnow()

        items = [
            NewsItem(1, "source1", "Title1", "http://link1", now, None, now, "hash1"),
            NewsItem(2, "source1", "Title2", "http://link2", now, None, now, "hash2"),
            NewsItem(3, "source2", "Title3", "http://link3", now, None, now, "hash3"),
        ]

        event = Event(id=1, items=items, created_at=now)

        source_ids = event.source_ids
        assert len(source_ids) == 2
        assert "source1" in source_ids
        assert "source2" in source_ids

    def test_event_canonical_title_auto(self):
        """Test that canonical title is automatically set to shortest."""
        now = datetime.utcnow()

        items = [
            NewsItem(1, "source1", "Very long article title here", "http://link1", now, None, now, "hash1"),
            NewsItem(2, "source2", "Short title", "http://link2", now, None, now, "hash2"),
            NewsItem(3, "source3", "Medium length title", "http://link3", now, None, now, "hash3"),
        ]

        event = Event(id=1, items=items, created_at=now)

        assert event.canonical_title == "Short title"

    def test_event_most_recent_time(self):
        """Test that most_recent_time returns the latest published_at."""
        from datetime import timedelta

        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        two_hours_ago = now - timedelta(hours=2)

        items = [
            NewsItem(1, "source1", "Title1", "http://link1", two_hours_ago, None, now, "hash1"),
            NewsItem(2, "source2", "Title2", "http://link2", now, None, now, "hash2"),
            NewsItem(3, "source3", "Title3", "http://link3", hour_ago, None, now, "hash3"),
        ]

        event = Event(id=1, items=items, created_at=now)

        assert event.most_recent_time == now
