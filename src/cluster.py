"""Article clustering to group similar news items into events."""

import logging
from typing import List, Dict, Any

from .models import NewsItem, Event
from .utils import title_similarity, load_yaml, get_config_path


logger = logging.getLogger(__name__)


def load_clustering_config() -> Dict[str, Any]:
    """Load clustering configuration from settings.yaml."""
    config = load_yaml(str(get_config_path('settings.yaml')))

    return {
        'similarity_threshold': config.get('similarity_threshold', 0.35),
        'financial_similarity_threshold': config.get('financial_similarity_threshold', 0.25),
        'min_sources_per_event': config.get('min_sources_per_event', 2),
        'financial_sources': set(config.get('financial_sources', [])),
    }


def _is_financial_item(item: NewsItem, financial_sources: set) -> bool:
    """Check if item is from a financial source."""
    return item.source_id in financial_sources


def cluster_items(items: List[NewsItem]) -> List[Event]:
    """
    Cluster news items into events based on title similarity.

    Uses greedy clustering algorithm:
    - Process items from newest to oldest
    - For each item, find most similar existing cluster
    - If similarity >= threshold, add to cluster
    - Otherwise, create new cluster

    Args:
        items: List of NewsItem objects to cluster

    Returns:
        List of Event objects (clusters)
    """
    config = load_clustering_config()
    threshold = config['similarity_threshold']
    min_sources = config['min_sources_per_event']

    if not items:
        return []

    logger.info(f"Clustering {len(items)} items (threshold={threshold}, min_sources={min_sources})")

    # Sort by published date (newest first)
    sorted_items = sorted(items, key=lambda x: x.published_at, reverse=True)

    # Initialize clusters (list of lists of items)
    clusters: List[List[NewsItem]] = []

    for item in sorted_items:
        # Determine if this is a financial item
        is_financial = _is_financial_item(item, config['financial_sources'])
        # Use lower threshold for financial items (more aggressive clustering)
        item_threshold = config['financial_similarity_threshold'] if is_financial else threshold

        # Find best matching cluster
        best_cluster_idx = None
        best_similarity = 0.0

        for idx, cluster in enumerate(clusters):
            # Check if cluster has same topic type (financial vs general)
            cluster_is_financial = any(_is_financial_item(c_item, config['financial_sources'])
                                      for c_item in cluster)

            # Only cluster with same topic type
            if is_financial != cluster_is_financial:
                continue

            # Calculate max similarity to any item in cluster
            max_sim = max(
                title_similarity(item.title, cluster_item.title)
                for cluster_item in cluster
            )

            if max_sim > best_similarity:
                best_similarity = max_sim
                best_cluster_idx = idx

        # Add to best cluster if similarity meets threshold
        if best_similarity >= item_threshold and best_cluster_idx is not None:
            clusters[best_cluster_idx].append(item)
        else:
            # Create new cluster
            clusters.append([item])

    logger.info(f"Created {len(clusters)} initial clusters")

    # Convert clusters to Event objects
    events = []
    for cluster_items in clusters:
        event = Event(
            id=None,  # Will be assigned by database
            items=cluster_items,
            created_at=cluster_items[0].published_at  # Use newest item's time
        )
        events.append(event)

    # Filter out single-source events (unless config allows)
    if min_sources > 1:
        filtered_events = [e for e in events if e.source_count >= min_sources]
        logger.info(f"Filtered to {len(filtered_events)} events with {min_sources}+ sources")
        events = filtered_events

    return events


def refine_canonical_title(event: Event) -> str:
    """
    Select the best canonical title for an event.

    Strategy:
    1. Prefer wire service (Reuters, AP) titles
    2. Otherwise, use shortest title (often clearest)

    Args:
        event: Event to select title for

    Returns:
        Canonical title string
    """
    if not event.items:
        return ""

    # Try to find a wire service title
    wire_items = [item for item in event.items if _is_wire_source(item.source_id)]

    if wire_items:
        # Use shortest wire service title
        return min(wire_items, key=lambda x: len(x.title)).title

    # Fall back to shortest title overall
    return min(event.items, key=lambda x: len(x.title)).title


def _is_wire_source(source_id: str) -> bool:
    """Check if a source is a wire service (Reuters, AP)."""
    wire_prefixes = ['reuters', 'ap']
    return any(source_id.startswith(prefix) for prefix in wire_prefixes)


def categorize_events(events: List[Event]) -> tuple[List[Event], List[Event]]:
    """
    Categorize events into general news and financial news.

    Returns:
        Tuple of (general_events, financial_events)
    """
    config = load_clustering_config()
    financial_sources = config['financial_sources']

    general_events = []
    financial_events = []

    for event in events:
        # Count how many items are from financial sources
        financial_count = sum(1 for item in event.items
                            if item.source_id in financial_sources)

        # If majority are financial sources, categorize as financial
        if financial_count > len(event.items) / 2:
            financial_events.append(event)
        else:
            general_events.append(event)

    return general_events, financial_events
