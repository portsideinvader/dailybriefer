# Quick Start Guide

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Generate Your First Brief

Run the generator:
```bash
python -m src.main
```

Or use the convenience script:
```bash
./generate_brief.sh
```

The brief will be written to [output/brief.md](output/brief.md).

## What Just Happened?

The system:
1. Fetched articles from 8 RSS feeds (Reuters, AP, BBC, NPR, Guardian, NYT, Economist)
2. Stored them in a local SQLite database with deduplication
3. Clustered similar articles into "events" using title similarity
4. Filtered to events reported by 2+ independent sources
5. Ranked events by source count, credibility, and recency
6. Generated a concise Markdown brief with the top 10 events

## Understanding the Brief

Each event shows:
- **Bold headline**: Canonical title (prefers wire services, then shortest)
- **Source links**: Clickable links to 2-5 sources reporting this story
- Sources are sorted by tier (wire > news > magazine)

## Customization

### Change Feed Sources

Edit [config/feeds.yaml](config/feeds.yaml):
- Add your preferred RSS feeds
- Set tier: `wire` (highest trust), `news`, or `magazine`
- Set region: `US`, `EU`, `Global`, etc.

### Adjust Settings

Edit [config/settings.yaml](config/settings.yaml):

**Key settings:**
- `lookback_hours: 24` - How far back to fetch articles
- `min_sources_per_event: 2` - Minimum sources required
- `max_events_in_brief: 10` - Maximum events to show
- `similarity_threshold: 0.35` - Clustering sensitivity (lower = more aggressive clustering)

**Source tier weights:**
```yaml
source_tier_weights:
  wire: 3.0      # Reuters, AP
  news: 2.0      # BBC, NPR, NYT, Guardian
  magazine: 1.0  # The Economist
```

## Scheduling (Optional)

### macOS/Linux (cron)

```bash
crontab -e
```

Add this line (run at 6 AM daily):
```
0 6 * * * cd /path/to/dailybriefer && /usr/bin/python3 -m src.main
```

### macOS (launchd) - More Reliable

Create `~/Library/LaunchAgents/com.dailybriefer.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.dailybriefer</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>-m</string>
        <string>src.main</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/path/to/dailybriefer</string>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>6</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/tmp/dailybriefer.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/dailybriefer.err</string>
</dict>
</plist>
```

Load it:
```bash
launchctl load ~/Library/LaunchAgents/com.dailybriefer.plist
```

## Running Tests

```bash
pytest
```

Or run specific test files:
```bash
pytest tests/test_utils.py -v
pytest tests/test_models.py -v
```

## Data Location

- **Database**: `data/news.db` (SQLite)
- **Latest brief**: `output/brief.md`
- **Archive**: `output/archive/brief_YYYY-MM-DD.md`

## Troubleshooting

### "No recent items to cluster"

This means no articles were published in the last 24 hours (or your lookback window). This is normal if:
- Running outside of peak news hours
- RSS feeds are temporarily unavailable
- Network connection issues

### Feed parsing warnings

Some feeds may have minor parsing issues but still work. The system logs warnings but continues processing.

### Want more events?

Reduce `min_sources_per_event` to 1 in settings.yaml (less trustworthy, more events).

Or increase `similarity_threshold` to cluster less aggressively (more separate events).

### Want fewer, more important events?

Increase `min_sources_per_event` to 3+ for higher confidence.

Decrease `max_events_in_brief` to show only top stories.

## Next Steps

1. Customize your feed sources in [config/feeds.yaml](config/feeds.yaml)
2. Adjust settings in [config/settings.yaml](config/settings.yaml)
3. Set up daily scheduling (cron/launchd)
4. Check [output/brief.md](output/brief.md) each morning

## Philosophy

This tool prioritizes **trustworthiness over completeness**:
- Multi-source verification required
- Wire services weighted higher
- Always includes source links
- No editorial commentary
- Factual summaries only

You're in control of what sources you trust and how the brief is generated.
