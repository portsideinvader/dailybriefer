# Daily Briefer - Demo & Quick Start

## What You Just Got

Your Daily Briefer now generates **two beautiful output formats**:

### 1. HTML Brief (Recommended) 📰
- Modern, card-based design
- Color-coded source credibility badges
- Click any source to read the full article
- Responsive (works on mobile too)
- Visual stats and importance scores

### 2. Markdown Brief 📝
- Plain text format
- Great for archival and searching
- Version control friendly
- Works anywhere

## Try It Now!

### Generate Your Brief

```bash
./generate_brief.sh
```

You'll see:
```
==========================================
📰 Your morning brief is ready!
==========================================

View formats:
  HTML (recommended): ./view_brief.sh
  or open: output/brief.html

  Markdown: cat output/brief.md
==========================================
```

### View the HTML Brief

```bash
./view_brief.sh
```

This opens a beautiful HTML page in your browser with:

**Header:**
- 📰 Morning Brief title
- Current date (e.g., "December 21, 2025")
- Generation time
- Event count

**Legend:**
- Color guide for source credibility
- Green = Wire services (highest trust)
- Blue = News organizations
- Purple = Magazines

**Event Cards:**
Each event shows:
- Event number (#1, #2, #3...)
- Importance score (0-10+)
- Large, readable headline
- Source count and article count
- Clickable source badges with credibility colors

**Footer Stats:**
- Total events
- Total articles analyzed
- Total source mentions

## HTML Features

### Visual Hierarchy
```
┌─────────────────────────────────────┐
│   📰 Morning Brief                  │ ← Purple gradient header
│   December 21, 2025                 │
│   🕐 Generated at 11:59 PM          │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Source Credibility                  │ ← Legend
│ 🟢 Wire Services                    │
│ 🔵 News Organizations              │
│ 🟣 Magazines                        │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ #1                     Score: 7.5   │ ← Event card
│                                     │
│ US pursuing third oil tanker        │ ← Headline
│ linked to Venezuela                 │
│                                     │
│ 2 sources • 2 articles             │ ← Metadata
│                                     │
│ [BBC News] [New York Times]        │ ← Source badges
└─────────────────────────────────────┘

[More event cards...]

┌─────────────────────────────────────┐
│          📊 Statistics              │ ← Footer
│   3 Events | 6 Articles | 6 Sources │
└─────────────────────────────────────┘
```

### Color Coding

**Wire Services (Green):**
- Reuters
- Associated Press (AP)
- Highest credibility

**News Organizations (Blue):**
- BBC
- NPR
- New York Times
- The Guardian

**Magazines (Purple):**
- The Economist

### Interactive Elements

- **Hover over event cards** → They lift up slightly
- **Click source badges** → Opens article in new tab
- **Responsive design** → Works on phone, tablet, desktop

## Set as Your Homepage

### Method 1: Browser Setting
1. Open browser settings
2. Set homepage to: `file:///Users/sebastianpucher/Tresor/Projects/dailybriefer/output/brief.html`
3. Your brief will be the first thing you see!

### Method 2: Schedule + Auto-Open

Add to crontab:
```bash
# Generate at 6 AM, open at 7 AM
0 6 * * * cd /path/to/dailybriefer && python3 -m src.main
0 7 * * * cd /path/to/dailybriefer && open output/brief.html
```

### Method 3: Keyboard Shortcut

Create an Alfred/Raycast workflow:
- Trigger: `brief` or custom hotkey
- Action: Run `cd /path/to/dailybriefer && ./view_brief.sh`

## Comparison: Markdown vs HTML

**Markdown is good for:**
- ✅ Searching with grep
- ✅ Version control
- ✅ Terminal viewing
- ✅ Automation/parsing

**HTML is better for:**
- ✅ Daily reading (much more engaging)
- ✅ Visual hierarchy (important events stand out)
- ✅ Quick scanning (color-coded sources)
- ✅ Mobile reading
- ✅ Credibility assessment at a glance

## Example Output

Your current brief shows:

**Event #1: US pursuing third oil tanker linked to Venezuela**
- Score: 7.5
- Sources: BBC World News (🔵), New York Times (🔵)

**Event #2: 9 killed, 10 wounded in South African pub shooting**
- Score: 6.4
- Sources: New York Times (🔵), NPR (🔵)

**Event #3: Israel approves 19 new settlements in occupied West Bank**
- Score: 6.2
- Sources: The Guardian (🔵), BBC World News (🔵)

All verified by multiple independent sources!

## Customization

### Change Colors

Edit [src/render_html.py](src/render_html.py), find the `:root` section:

```css
:root {
    --color-accent: #3498db;      /* Main accent color */
    --color-wire: #27ae60;        /* Wire badge (green) */
    --color-news: #3498db;        /* News badge (blue) */
    --color-magazine: #9b59b6;    /* Magazine badge (purple) */
}
```

### Change Layout Width

Find and edit:
```css
.container {
    max-width: 900px;  /* Make wider or narrower */
}
```

### Change Header Gradient

Find and edit:
```css
.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    /* Try: #FF6B6B to #4ECDC4 for red-to-teal */
    /* Try: #F857A6 to #FF5858 for pink-to-red */
}
```

## Files Generated

```
output/
├── brief.html          # Beautiful HTML (13KB) - Your main brief
├── brief.md           # Plain Markdown (1KB) - For searching
└── archive/
    └── brief_2025-12-21.md  # Archived copy
```

## Tips for Daily Use

1. **Bookmark the HTML file** for instant access
2. **Set it as your browser homepage** (see above)
3. **Run generate_brief.sh each morning** (or schedule it)
4. **Keep both formats** - HTML for reading, Markdown for searching old briefs
5. **Share via email** if needed (HTML file is self-contained)

## Why This is Better Than News Apps

| Feature | News Apps | Daily Briefer HTML |
|---------|-----------|-------------------|
| Cost | $$ subscription | **Free** |
| Privacy | Tracks you | **Local only** |
| Ads | Yes | **None** |
| Algorithm | Black box | **Transparent** |
| Multi-source | No | **Yes (required)** |
| Credibility | Mixed | **Wire services prioritized** |
| Customizable | No | **Fully customizable** |

Enjoy your beautiful, trustworthy morning news brief! 📰✨
