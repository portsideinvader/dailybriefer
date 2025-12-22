"""Main CLI entrypoint for Daily Briefer."""

import logging
import sys
from datetime import datetime

from .ingest import fetch_all_feeds, load_sources
from .store import NewsDatabase
from .cluster import cluster_items, refine_canonical_title
from .rank import select_top_events
from .render import render_brief, archive_brief
from .render_html import render_html_brief
from .utils import load_yaml, get_config_path


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main pipeline execution."""
    logger.info("=" * 60)
    logger.info("Daily Briefer - Starting")
    logger.info("=" * 60)

    try:
        # Load configuration
        settings = load_yaml(str(get_config_path('settings.yaml')))
        lookback_hours = settings.get('lookback_hours', 24)

        # Initialize database
        db = NewsDatabase()
        db.connect()

        # Step 1: Upsert sources
        logger.info("Step 1: Loading source configurations")
        sources = load_sources()
        for source in sources:
            db.upsert_source(source)
        logger.info(f"  Loaded {len(sources)} sources")

        # Step 2: Ingest RSS feeds
        logger.info("Step 2: Fetching RSS feeds")
        new_items = fetch_all_feeds()

        # Step 3: Store items (with deduplication)
        logger.info("Step 3: Storing items in database")
        stored_count = 0
        duplicate_count = 0

        for item in new_items:
            item_id = db.insert_item(item)
            if item_id is not None:
                stored_count += 1
            else:
                duplicate_count += 1

        logger.info(f"  Stored {stored_count} new items, skipped {duplicate_count} duplicates")

        # Step 4: Retrieve recent items for clustering
        logger.info(f"Step 4: Retrieving items from last {lookback_hours} hours")
        recent_items = db.get_recent_items(hours=lookback_hours)
        logger.info(f"  Found {len(recent_items)} recent items")

        if not recent_items:
            logger.warning("No recent items to cluster. Exiting.")
            render_brief([])  # Generate empty brief
            db.close()
            return 0

        # Step 5: Cluster items into events
        logger.info("Step 5: Clustering items into events")
        events = cluster_items(recent_items)

        # Refine canonical titles
        for event in events:
            event.canonical_title = refine_canonical_title(event)

        # Step 6: Rank and select top events
        logger.info("Step 6: Ranking events")
        top_events = select_top_events(events)

        # Step 7: Store events in database
        logger.info("Step 7: Storing events in database")
        for event in top_events:
            item_ids = [item.id for item in event.items]
            event_id = db.create_event(
                item_ids=item_ids,
                score=event.score,
                canonical_title=event.canonical_title
            )
            event.id = event_id

        # Step 8: Render briefs (Markdown and HTML)
        logger.info("Step 8: Rendering morning brief")
        render_brief(top_events)
        render_html_brief(top_events)

        # Step 9: Archive (optional)
        logger.info("Step 9: Archiving brief")
        archive_brief()

        # Clean up old events (keep 7 days)
        logger.info("Step 10: Cleaning up old events")
        db.clear_old_events(keep_days=7)

        # Close database
        db.close()

        logger.info("=" * 60)
        logger.info("Daily Briefer - Completed Successfully")
        logger.info("=" * 60)

        return 0

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
