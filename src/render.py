"""Markdown brief rendering."""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from .models import Event, NewsItem
from .utils import load_yaml, get_config_path, get_output_path, ensure_directory
from .ingest import load_sources


logger = logging.getLogger(__name__)


def load_render_config() -> Dict[str, Any]:
    """Load rendering configuration from settings.yaml."""
    config = load_yaml(str(get_config_path('settings.yaml')))

    return {
        'max_sources_per_event': config.get('max_sources_per_event', 5),
    }


def get_source_name_map() -> Dict[str, str]:
    """Build a map of source_id -> name."""
    sources = load_sources()
    return {source.id: source.name for source in sources}


def render_event(event: Event, source_names: Dict[str, str],
                config: Dict[str, Any]) -> str:
    """
    Render a single event as Markdown.

    Format:
    - **Canonical headline**
      - [Source1](url1), [Source2](url2), [Source3](url3)

    Args:
        event: Event to render
        source_names: Map of source_id -> display name
        config: Rendering configuration

    Returns:
        Markdown string
    """
    max_sources = config['max_sources_per_event']

    # Build the headline
    headline = event.canonical_title

    # Sort items by source tier (wire first) and then by published date
    sorted_items = sorted(
        event.items,
        key=lambda x: (
            _get_source_tier_priority(x.source_id),
            x.published_at
        ),
        reverse=True
    )

    # Limit sources displayed
    display_items = sorted_items[:max_sources]
    remaining_count = len(event.items) - len(display_items)

    # Build source links
    source_links = []
    for item in display_items:
        source_name = source_names.get(item.source_id, item.source_id)
        source_links.append(f"[{source_name}]({item.link})")

    source_line = ", ".join(source_links)

    if remaining_count > 0:
        source_line += f" (+{remaining_count} more)"

    # Format as Markdown
    md = f"- **{headline}**\n"
    md += f"  - {source_line}\n"

    return md


def _get_source_tier_priority(source_id: str) -> int:
    """
    Get sort priority for source tier (higher = better).

    Wire services first, then news, then magazine.
    """
    if source_id.startswith('reuters') or source_id.startswith('ap'):
        return 3
    elif 'magazine' in source_id or 'economist' in source_id:
        return 1
    else:
        return 2


def render_brief(events: List[Event], output_path: Optional[Path] = None) -> str:
    """
    Render complete morning brief as Markdown.

    Args:
        events: List of Event objects to include (should already be ranked/filtered)
        output_path: Path to write output file (default: output/brief.md)

    Returns:
        Markdown string
    """
    if output_path is None:
        output_path = get_output_path('brief.md')

    config = load_render_config()
    source_names = get_source_name_map()

    # Build header
    today = datetime.now().strftime('%Y-%m-%d')
    md_lines = [
        f"# Morning Brief — {today}",
        "",
        f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
        "",
    ]

    # Render each event
    if events:
        for event in events:
            event_md = render_event(event, source_names, config)
            md_lines.append(event_md)
    else:
        md_lines.append("*No events to report.*")
        md_lines.append("")

    # Footer with stats
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")
    md_lines.append(f"**Stats**: {len(events)} events")

    if events:
        total_sources = sum(e.source_count for e in events)
        total_items = sum(len(e.items) for e in events)
        md_lines.append(f" | {total_items} articles | {total_sources} distinct source mentions")

    md_lines.append("")

    # Join into final markdown
    markdown = "\n".join(md_lines)

    # Write to file
    ensure_directory(str(output_path.parent))

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown)

    logger.info(f"Brief written to {output_path}")

    return markdown


def archive_brief(date: Optional[datetime] = None) -> None:
    """
    Copy current brief to archive with date stamp.

    Args:
        date: Date to use in archive filename (default: today)
    """
    if date is None:
        date = datetime.now()

    date_str = date.strftime('%Y-%m-%d')
    archive_filename = f"brief_{date_str}.md"

    source_path = get_output_path('brief.md')
    archive_path = get_output_path(f'archive/{archive_filename}')

    if not source_path.exists():
        logger.warning("No brief to archive")
        return

    # Ensure archive directory exists
    ensure_directory(str(archive_path.parent))

    # Copy file
    import shutil
    shutil.copy2(source_path, archive_path)

    logger.info(f"Archived brief to {archive_path}")
