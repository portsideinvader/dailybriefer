"""HTML brief rendering with modern styling."""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from .models import Event, NewsItem
from .utils import load_yaml, get_config_path, get_output_path, ensure_directory
from .ingest import load_sources
from .cluster import categorize_events


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


def get_source_tier_map() -> Dict[str, str]:
    """Build a map of source_id -> tier."""
    sources = load_sources()
    return {source.id: source.tier for source in sources}


def _get_tier_badge_class(tier: str) -> str:
    """Get CSS class for tier badge."""
    tier_classes = {
        'wire': 'badge-wire',
        'news': 'badge-news',
        'magazine': 'badge-magazine'
    }
    return tier_classes.get(tier, 'badge-news')


def render_event_html(event: Event, source_names: Dict[str, str],
                      source_tiers: Dict[str, str], config: Dict[str, Any],
                      index: int) -> str:
    """
    Render a single event as HTML card.

    Args:
        event: Event to render
        source_names: Map of source_id -> display name
        source_tiers: Map of source_id -> tier
        config: Rendering configuration
        index: Event index (for numbering)

    Returns:
        HTML string
    """
    max_sources = config['max_sources_per_event']

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

    # Build source links HTML
    source_links_html = []
    for item in display_items:
        source_name = source_names.get(item.source_id, item.source_id)
        tier = source_tiers.get(item.source_id, 'news')
        badge_class = _get_tier_badge_class(tier)

        source_links_html.append(f'''
            <a href="{item.link}" target="_blank" class="source-link" rel="noopener noreferrer">
                <span class="source-badge {badge_class}">{source_name}</span>
            </a>
        ''')

    sources_html = ''.join(source_links_html)

    if remaining_count > 0:
        sources_html += f'<span class="more-sources">+{remaining_count} more</span>'

    # Get event score for display
    score_display = f"{event.score:.1f}" if event.score > 0 else "—"

    html = f'''
    <div class="event-card">
        <div class="event-header">
            <span class="event-number">#{index}</span>
            <span class="event-score" title="Importance score based on sources, credibility, and recency">
                Score: {score_display}
            </span>
        </div>
        <h2 class="event-title">{event.canonical_title}</h2>
        <div class="event-meta">
            <span class="source-count">{event.source_count} source{'s' if event.source_count > 1 else ''}</span>
            <span class="article-count">{len(event.items)} article{'s' if len(event.items) > 1 else ''}</span>
        </div>
        <div class="event-sources">
            {sources_html}
        </div>
    </div>
    '''

    return html


def _get_source_tier_priority(source_id: str) -> int:
    """Get sort priority for source tier (higher = better)."""
    if source_id.startswith('reuters') or source_id.startswith('ap'):
        return 3
    elif 'magazine' in source_id or 'economist' in source_id:
        return 1
    else:
        return 2


def render_html_brief(events: List[Event], output_path: Optional[Path] = None) -> str:
    """
    Render complete morning brief as HTML.

    Args:
        events: List of Event objects to include (should already be ranked/filtered)
        output_path: Path to write output file (default: output/brief.html)

    Returns:
        HTML string
    """
    if output_path is None:
        output_path = get_output_path('brief.html')

    config = load_render_config()
    source_names = get_source_name_map()
    source_tiers = get_source_tier_map()

    # Build header
    today = datetime.now().strftime('%B %d, %Y')
    time_generated = datetime.now().strftime('%I:%M %p')

    # Categorize events into general and financial
    general_events, financial_events = categorize_events(events)

    # Render general news section
    general_html = []
    if general_events:
        for idx, event in enumerate(general_events, 1):
            event_html = render_event_html(event, source_names, source_tiers, config, idx)
            general_html.append(event_html)
    else:
        general_html.append('<div class="no-events">No general news events today.</div>')

    general_content = '\n'.join(general_html)

    # Render financial news section
    financial_html = []
    if financial_events:
        for idx, event in enumerate(financial_events, 1):
            event_html = render_event_html(event, source_names, source_tiers, config, idx)
            financial_html.append(event_html)
    else:
        financial_html.append('<div class="no-events">No financial news events today.</div>')

    financial_content = '\n'.join(financial_html)

    # Calculate stats
    total_sources = sum(e.source_count for e in events) if events else 0
    total_items = sum(len(e.items) for e in events) if events else 0

    # Build complete HTML
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Morning Brief — {today}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        :root {{
            --color-bg: #f5f7fa;
            --color-surface: #ffffff;
            --color-primary: #2c3e50;
            --color-secondary: #7f8c8d;
            --color-accent: #3498db;
            --color-wire: #27ae60;
            --color-news: #3498db;
            --color-magazine: #9b59b6;
            --color-border: #e1e8ed;
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.06);
            --shadow-md: 0 4px 6px rgba(0,0,0,0.07);
            --shadow-lg: 0 10px 20px rgba(0,0,0,0.1);
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: var(--color-bg);
            color: var(--color-primary);
            line-height: 1.6;
            padding: 20px;
        }}

        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            border-radius: 16px;
            margin-bottom: 30px;
            box-shadow: var(--shadow-lg);
        }}

        .header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 8px;
        }}

        .header-meta {{
            font-size: 1rem;
            opacity: 0.95;
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            margin-top: 12px;
        }}

        .header-meta-item {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .events-container {{
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}

        .event-card {{
            background: var(--color-surface);
            border-radius: 12px;
            padding: 24px;
            box-shadow: var(--shadow-md);
            transition: transform 0.2s, box-shadow 0.2s;
            border: 1px solid var(--color-border);
        }}

        .event-card:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }}

        .event-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }}

        .event-number {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 32px;
            height: 32px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.9rem;
        }}

        .event-score {{
            font-size: 0.85rem;
            color: var(--color-secondary);
            font-weight: 500;
        }}

        .event-title {{
            font-size: 1.4rem;
            font-weight: 600;
            color: var(--color-primary);
            margin-bottom: 12px;
            line-height: 1.4;
        }}

        .event-meta {{
            display: flex;
            gap: 16px;
            margin-bottom: 16px;
            font-size: 0.9rem;
            color: var(--color-secondary);
        }}

        .event-sources {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            align-items: center;
        }}

        .source-link {{
            text-decoration: none;
            transition: transform 0.2s;
            display: inline-block;
        }}

        .source-link:hover {{
            transform: translateY(-1px);
        }}

        .source-badge {{
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;
            color: white;
            transition: opacity 0.2s;
        }}

        .source-link:hover .source-badge {{
            opacity: 0.9;
        }}

        .badge-wire {{
            background: linear-gradient(135deg, #27ae60 0%, #229954 100%);
        }}

        .badge-news {{
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        }}

        .badge-magazine {{
            background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%);
        }}

        .more-sources {{
            display: inline-block;
            padding: 6px 14px;
            background: var(--color-border);
            color: var(--color-secondary);
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;
        }}

        .footer {{
            margin-top: 40px;
            padding: 30px;
            background: var(--color-surface);
            border-radius: 12px;
            text-align: center;
            border: 1px solid var(--color-border);
            box-shadow: var(--shadow-sm);
        }}

        .footer-stats {{
            display: flex;
            justify-content: center;
            gap: 40px;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }}

        .stat {{
            text-align: center;
        }}

        .stat-value {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--color-accent);
            display: block;
        }}

        .stat-label {{
            font-size: 0.9rem;
            color: var(--color-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .footer-note {{
            font-size: 0.85rem;
            color: var(--color-secondary);
            margin-top: 16px;
        }}

        .no-events {{
            text-align: center;
            padding: 60px 20px;
            color: var(--color-secondary);
            font-size: 1.1rem;
        }}

        .section-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 40px 0 20px 0;
            padding-bottom: 12px;
            border-bottom: 3px solid;
            border-image: linear-gradient(90deg, #667eea 0%, #764ba2 100%) 1;
        }}

        .section-header:first-of-type {{
            margin-top: 0;
        }}

        .section-title {{
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--color-primary);
        }}

        .section-count {{
            font-size: 1rem;
            color: var(--color-secondary);
            font-weight: 500;
        }}

        .legend {{
            background: var(--color-surface);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            border: 1px solid var(--color-border);
        }}

        .legend-title {{
            font-size: 0.9rem;
            font-weight: 600;
            color: var(--color-secondary);
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .legend-items {{
            display: flex;
            gap: 16px;
            flex-wrap: wrap;
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.85rem;
        }}

        .legend-badge {{
            width: 12px;
            height: 12px;
            border-radius: 3px;
        }}

        @media (max-width: 600px) {{
            .header h1 {{
                font-size: 2rem;
            }}

            .event-title {{
                font-size: 1.2rem;
            }}

            .footer-stats {{
                gap: 20px;
            }}

            .stat-value {{
                font-size: 1.5rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📰 Morning Brief</h1>
            <div>{today}</div>
            <div class="header-meta">
                <div class="header-meta-item">
                    <span>🕐</span>
                    <span>Generated at {time_generated}</span>
                </div>
                <div class="header-meta-item">
                    <span>📊</span>
                    <span>{len(events)} top {'event' if len(events) == 1 else 'events'}</span>
                </div>
            </div>
        </div>

        <div class="legend">
            <div class="legend-title">Source Credibility</div>
            <div class="legend-items">
                <div class="legend-item">
                    <div class="legend-badge" style="background: linear-gradient(135deg, #27ae60 0%, #229954 100%);"></div>
                    <span>Wire Services (Reuters, AP) — Highest credibility</span>
                </div>
                <div class="legend-item">
                    <div class="legend-badge" style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);"></div>
                    <span>News Organizations (BBC, NPR, NYT, Guardian)</span>
                </div>
                <div class="legend-item">
                    <div class="legend-badge" style="background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%);"></div>
                    <span>Magazines (The Economist)</span>
                </div>
            </div>
        </div>

        <!-- General World News Section -->
        <div class="section-header">
            <h2 class="section-title">🌍 General World News</h2>
            <span class="section-count">{len(general_events)} events</span>
        </div>
        <div class="events-container">
            {general_content}
        </div>

        <!-- Financial & Economics Section -->
        <div class="section-header">
            <h2 class="section-title">💼 Finance & Economics</h2>
            <span class="section-count">{len(financial_events)} events</span>
        </div>
        <div class="events-container">
            {financial_content}
        </div>

        <div class="footer">
            <div class="footer-stats">
                <div class="stat">
                    <span class="stat-value">{len(events)}</span>
                    <span class="stat-label">Events</span>
                </div>
                <div class="stat">
                    <span class="stat-value">{total_items}</span>
                    <span class="stat-label">Articles</span>
                </div>
                <div class="stat">
                    <span class="stat-value">{total_sources}</span>
                    <span class="stat-label">Source Mentions</span>
                </div>
            </div>
            <div class="footer-note">
                All events verified by multiple independent sources • Click any source to read the full article
            </div>
        </div>
    </div>
</body>
</html>
'''

    # Write to file
    ensure_directory(str(output_path.parent))

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    logger.info(f"HTML brief written to {output_path}")

    return html
