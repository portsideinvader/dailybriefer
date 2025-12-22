"""RSS feed ingestion module."""

import logging
from datetime import datetime, timezone
from typing import Any, List

import feedparser
from dateutil import parser as date_parser

from .models import Source, NewsItem
from .utils import make_guid_hash, load_yaml, get_config_path


logger = logging.getLogger(__name__)


def load_sources() -> List[Source]:
    """Load source configurations from feeds.yaml."""
    config = load_yaml(str(get_config_path('feeds.yaml')))

    sources = []
    for feed_config in config.get('feeds', []):
        sources.append(Source(
            id=feed_config['id'],
            name=feed_config['name'],
            rss_url=feed_config['rss_url'],
            tier=feed_config['tier'],
            region=feed_config['region']
        ))

    return sources


def fetch_feed(source: Source) -> List[NewsItem]:
    """
    Fetch and parse RSS feed for a single source.

    Args:
        source: Source to fetch from

    Returns:
        List of NewsItem objects
    """
    logger.info(f"Fetching feed: {source.name} ({source.rss_url})")

    try:
        feed = feedparser.parse(source.rss_url)

        if feed.bozo:
            # Feed has parsing errors
            logger.warning(f"Feed parsing issues for {source.name}: {feed.bozo_exception}")

        items = []
        # Use replace to make timezone-naive for database storage
        fetched_at = datetime.now(timezone.utc).replace(tzinfo=None)

        for entry in feed.entries:
            try:
                item = _parse_entry(entry, source, fetched_at)
                if item:
                    items.append(item)
            except Exception as e:
                logger.error(f"Error parsing entry from {source.name}: {e}")
                continue

        logger.info(f"Fetched {len(items)} items from {source.name}")
        return items

    except Exception as e:
        logger.error(f"Failed to fetch feed {source.name}: {e}")
        return []


def _parse_entry(entry: Any, source: Source, fetched_at: datetime) -> NewsItem:
    """
    Parse a single feed entry into a NewsItem.

    Args:
        entry: feedparser entry object
        source: Source this entry came from
        fetched_at: Timestamp when feed was fetched

    Returns:
        NewsItem object or None if parsing fails
    """
    # Extract title
    title = entry.get('title', '').strip()
    if not title:
        logger.warning(f"Entry missing title from {source.name}")
        return None

    # Extract link
    link = entry.get('link', '').strip()
    if not link:
        logger.warning(f"Entry missing link from {source.name}: {title}")
        return None

    # Extract published date
    published_at = _parse_published_date(entry, fetched_at)

    # Extract summary/description
    summary = entry.get('summary', entry.get('description', '')).strip()

    # Create GUID hash for deduplication
    # Prefer entry.id, fall back to link
    guid = entry.get('id', link)
    guid_hash = make_guid_hash(guid)

    return NewsItem(
        id=None,  # Will be assigned by database
        source_id=source.id,
        title=title,
        link=link,
        published_at=published_at,
        summary=summary if summary else None,
        fetched_at=fetched_at,
        guid_hash=guid_hash
    )


def _parse_published_date(entry: Any, fallback: datetime) -> datetime:
    """
    Extract and parse published date from feed entry.

    Args:
        entry: feedparser entry object
        fallback: Fallback datetime if parsing fails

    Returns:
        datetime object
    """
    # Try multiple date fields in order of preference
    date_fields = ['published_parsed', 'updated_parsed', 'created_parsed']

    for field in date_fields:
        if field in entry and entry[field]:
            try:
                # feedparser gives us time.struct_time
                time_struct = entry[field]
                return datetime(*time_struct[:6])
            except Exception:
                pass

    # Try string date fields
    string_fields = ['published', 'updated', 'created']
    for field in string_fields:
        if field in entry and entry[field]:
            try:
                return date_parser.parse(entry[field])
            except Exception:
                pass

    # Fall back to fetched time
    logger.warning(f"Could not parse date for entry, using fallback: {entry.get('title', '')}")
    return fallback


def fetch_all_feeds() -> List[NewsItem]:
    """
    Fetch items from all configured feeds.

    Returns:
        List of all NewsItem objects from all sources
    """
    sources = load_sources()
    all_items = []

    logger.info(f"Fetching {len(sources)} feeds...")

    for source in sources:
        items = fetch_feed(source)
        all_items.extend(items)

    logger.info(f"Total items fetched: {len(all_items)}")
    return all_items
