# Daily Briefer 📰

**Your Personal Objective Morning News Brief**

A local-first, $0 budget news aggregator that generates trustworthy daily briefs from 14 premium RSS sources with multi-source verification.

## Features

✅ **Two-Section Brief**
- 🌍 General World News (BBC, NYT, Guardian, NPR, Reuters, AP)
- 💼 Finance & Economics (WSJ, FT, Bloomberg, CNBC, MarketWatch)

✅ **Multi-Source Verification**
- Minimum 2 sources required per event
- Protects against single-source bias
- Topic-aware clustering (financial news clusters separately)

✅ **Beautiful Output**
- Modern HTML with gradient headers
- Card-based event design
- Color-coded source badges by tier
- Mobile-responsive
- Also generates Markdown

✅ **Smart Ranking**
- Source tier weighting (wire > news > magazine)
- Recency scoring
- Event importance calculated from multiple sources

✅ **Deploy as Webpage**
- Publish to GitHub Pages (free)
- Automatic daily updates
- Access from any device
- Still $0 cost

## Installation

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

### Local Generation

```bash
# Generate brief
./generate_brief.sh

# View in browser
./view_brief.sh
```

Your brief appears in `output/`:
- `brief.html` - Beautiful web page with sections
- `brief.md` - Markdown version

### Deploy as Webpage

See [DEPLOY_AS_WEBPAGE.md](DEPLOY_AS_WEBPAGE.md) for full instructions.

**Quick version:**
1. Push to GitHub
2. Enable GitHub Pages (Settings → Pages → Deploy from `/docs`)
3. Access at `https://yourusername.github.io/dailybriefer/`
4. Automatic daily updates at 6 AM UTC

## Configuration

### Feed Sources

Edit [config/feeds.yaml](config/feeds.yaml) to add, remove, or modify RSS feeds.

Each feed has:
- `id`: Unique identifier
- `name`: Display name
- `rss_url`: RSS feed URL
- `tier`: `wire` (highest trust), `news`, or `magazine`
- `region`: `US`, `EU`, `Global`, etc.

### Settings

Edit [config/settings.yaml](config/settings.yaml) to adjust:

```yaml
# General news clustering (higher = stricter)
similarity_threshold: 0.35

# Financial news clustering (lower = more events)
financial_similarity_threshold: 0.25

# Multi-source requirement
min_sources_per_event: 2

# Event limit
max_events_in_brief: 20
```

## How It Works

### Pipeline

```
1. Fetch RSS feeds (14 sources)
   ↓
2. Store in local SQLite database
   ↓
3. Deduplicate by GUID
   ↓
4. Cluster similar articles (Jaccard similarity)
   ↓
5. Topic-aware clustering (financial vs general)
   ↓
6. Filter events with <2 sources
   ↓
7. Rank by importance
   ↓
8. Categorize into sections
   ↓
9. Render HTML & Markdown
```

### Topic-Aware Clustering

Financial stories use a **lower threshold (0.25)** to cluster more aggressively:

```
WSJ: "Tesla earnings disappoint"
Bloomberg: "Tesla misses targets"
→ Similarity: 0.28
→ Threshold: 0.25 (financial)
→ CLUSTERED! ✅
```

General news uses **higher threshold (0.35)** for quality:

```
BBC: "Tesla factory strike"
NYT: "Tesla workers protest"
→ Similarity: 0.32
→ Threshold: 0.35 (general)
→ NOT CLUSTERED ❌
```

Financial and general stories **never cluster together**, ensuring proper categorization.

## Current Sources (14)

### Wire Services (Tier 1)
- Reuters World News
- Reuters U.S. News
- AP Top News

### News Organizations (Tier 2)

**General:**
- BBC World News
- The Guardian World
- New York Times World
- NPR News

**Financial:**
- Wall Street Journal World
- Wall Street Journal Business
- Financial Times World
- Bloomberg Markets
- CNBC Top News
- MarketWatch

### Magazines (Tier 3)
- The Economist

## Project Structure

```
dailybriefer/
├── config/
│   ├── feeds.yaml       # RSS feed sources
│   └── settings.yaml    # Configuration
├── data/
│   └── news.db         # SQLite database (created on first run)
├── output/
│   ├── brief.md        # Latest generated brief
│   └── archive/        # Historical briefs (optional)
├── src/
│   ├── main.py         # CLI entrypoint
│   ├── ingest.py       # RSS fetching
│   ├── store.py        # Database operations
│   ├── cluster.py      # Article clustering
│   ├── rank.py         # Event ranking
│   ├── render.py       # Brief generation
│   ├── models.py       # Data models
│   └── utils.py        # Utilities
└── tests/              # Unit tests
```

## Objectivity Safeguards

- Events require minimum 2 distinct sources (configurable)
- All events include source links for verification
- Wire services (Reuters, AP) weighted higher
- No editorial commentary in MVP
- Factual summaries only

## Future Enhancements (Optional)

- TF-IDF or embedding-based clustering
- Local LLM summarization (Ollama)
- Conflict detection between sources
- Topic categorization
- Archive search

## License

Personal use project. Use at your own discretion.
