"""Event ranking and scoring to prioritize most important news."""

import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
import math

from .models import Event, Source
from .utils import load_yaml, get_config_path
from .ingest import load_sources


logger = logging.getLogger(__name__)


def load_ranking_config() -> Dict[str, Any]:
    """Load ranking configuration from settings.yaml."""
    config = load_yaml(str(get_config_path('settings.yaml')))

    return {
        'source_tier_weights': config.get('source_tier_weights', {
            'wire': 3.0,
            'news': 2.0,
            'magazine': 1.0
        }),
        'recency_weight': config.get('recency_weight', 0.1),
        'max_events_in_brief': config.get('max_events_in_brief', 10),
    }


def get_source_tier_map() -> Dict[str, str]:
    """Build a map of source_id -> tier."""
    sources = load_sources()
    return {source.id: source.tier for source in sources}


def calculate_event_score(event: Event, config: Dict[str, Any],
                          source_tiers: Dict[str, str]) -> float:
    """
    Calculate importance score for an event.

    Scoring factors:
    1. Source count (primary): More sources = more important
    2. Source tier weights: Wire services > newspapers > magazines
    3. Recency: Newer articles weighted higher

    Args:
        event: Event to score
        config: Ranking configuration
        source_tiers: Map of source_id -> tier

    Returns:
        Score (higher = more important)
    """
    # Base score: number of distinct sources
    base_score = float(event.source_count)

    # Tier weighting: sum weights of all sources
    tier_weights = config['source_tier_weights']
    tier_bonus = 0.0

    for source_id in event.source_ids:
        tier = source_tiers.get(source_id, 'news')  # Default to 'news'
        tier_bonus += tier_weights.get(tier, 1.0)

    # Average tier weight as multiplier
    avg_tier_weight = tier_bonus / event.source_count if event.source_count > 0 else 1.0

    # Recency bonus: exponential decay
    recency_weight = config['recency_weight']
    # Use replace to make timezone-naive for comparison with database datetimes
    current_time = datetime.now(timezone.utc).replace(tzinfo=None)
    hours_old = (current_time - event.most_recent_time).total_seconds() / 3600
    recency_factor = math.exp(-recency_weight * hours_old)

    # Combined score
    score = base_score * avg_tier_weight * (1 + recency_factor)

    return score


def rank_events(events: List[Event]) -> List[Event]:
    """
    Rank events by importance and return sorted list.

    Args:
        events: List of Event objects to rank

    Returns:
        List of Event objects sorted by score (highest first)
    """
    if not events:
        return []

    config = load_ranking_config()
    source_tiers = get_source_tier_map()

    logger.info(f"Ranking {len(events)} events")

    # Calculate scores
    for event in events:
        event.score = calculate_event_score(event, config, source_tiers)

    # Sort by score (descending)
    ranked_events = sorted(events, key=lambda e: e.score, reverse=True)

    # Log top events for debugging
    for i, event in enumerate(ranked_events[:5], 1):
        logger.info(
            f"  {i}. Score={event.score:.2f}, Sources={event.source_count}, "
            f"Title={event.canonical_title[:60]}..."
        )

    return ranked_events


def select_top_events(events: List[Event], max_count: Optional[int] = None) -> List[Event]:
    """
    Select top N events for the brief.

    Args:
        events: List of ranked Event objects
        max_count: Maximum number of events (uses config if None)

    Returns:
        List of top Event objects
    """
    config = load_ranking_config()

    if max_count is None:
        max_count = config['max_events_in_brief']

    # Rank events first
    ranked = rank_events(events)

    # Select top N
    top_events = ranked[:max_count]

    logger.info(f"Selected top {len(top_events)} events for brief")

    return top_events
