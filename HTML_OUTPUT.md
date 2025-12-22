# HTML Output Feature

## Overview

Your Daily Briefer now generates **beautiful HTML briefs** in addition to Markdown! The HTML version features modern styling with cards, badges, and interactive elements for a much more engaging reading experience.

## Features

### 🎨 Modern Design
- Clean, card-based layout
- Gradient headers with purple/blue theme
- Responsive design (works on mobile too)
- Smooth hover effects and transitions

### 🏷️ Source Credibility Badges
- **Green badges** = Wire services (Reuters, AP) - Highest credibility
- **Blue badges** = News organizations (BBC, NPR, NYT, Guardian)
- **Purple badges** = Magazines (The Economist)

### 📊 Visual Hierarchy
- Event numbering (#1, #2, #3...)
- Importance scores displayed
- Source and article counts per event
- Overall statistics at the bottom

### 🔗 Interactive Elements
- Click any source badge to read the full article
- Hover effects on cards and links
- Clean, readable typography
- Color-coded credibility system

## How to Use

### Generate the Brief

```bash
# Standard way
python -m src.main

# Or use the convenience script
./generate_brief.sh
```

This will create both:
- `output/brief.html` (recommended for reading)
- `output/brief.md` (for archival/grep)

### View the Brief

```bash
# Open HTML in your browser
./view_brief.sh

# Or manually
open output/brief.html
```

### Set as Daily Homepage

**Option 1: Browser Start Page**
1. Open your browser settings
2. Set start page to: `file:///Users/sebastianpucher/Tresor/Projects/dailybriefer/output/brief.html`
3. Your brief will be the first thing you see when opening your browser

**Option 2: Alfred/Raycast Shortcut**
Create a workflow that runs:
```bash
cd /path/to/dailybriefer && ./view_brief.sh
```

**Option 3: Keyboard Shortcut (macOS)**
Use Automator to create a service that runs the view script with a hotkey.

## Scheduled Workflow Example

```bash
# Cron job that generates at 6 AM and opens at 7 AM
0 6 * * * cd /path/to/dailybriefer && python3 -m src.main
0 7 * * * cd /path/to/dailybriefer && open output/brief.html
```

## Design Philosophy

The HTML output follows these principles:

1. **Information Hierarchy**: Most important info (headline) is largest
2. **Credibility First**: Wire sources prominently displayed
3. **Minimal Cognitive Load**: Clean, uncluttered design
4. **Action-Oriented**: One click to read full article
5. **Trust Signals**: Source counts, credibility badges, importance scores

## Customization

The HTML is generated in [src/render_html.py](src/render_html.py). You can customize:

### Colors

Edit the CSS `:root` variables:
```css
:root {
    --color-accent: #3498db;      /* Change accent color */
    --color-wire: #27ae60;        /* Wire service badge color */
    --color-news: #3498db;        /* News badge color */
    --color-magazine: #9b59b6;    /* Magazine badge color */
}
```

### Layout

- Change `max-width: 900px` for wider/narrower layout
- Adjust padding in `.event-card` for more/less spacing
- Modify gradient in `.header` for different header colors

### Font

Change the `font-family` in `body` to your preferred font.

## Screenshot Description

The HTML brief includes:

1. **Header Section**
   - Large title with emoji
   - Current date
   - Generation time
   - Event count

2. **Legend**
   - Color-coded guide to source credibility
   - Explains the badge system

3. **Event Cards**
   - Numbered events (#1, #2, #3...)
   - Importance score
   - Large, readable headline
   - Metadata (source count, article count)
   - Clickable source badges with credibility colors

4. **Footer Statistics**
   - Total events
   - Total articles analyzed
   - Total source mentions

## Benefits Over Markdown

| Feature | Markdown | HTML |
|---------|----------|------|
| Visual hierarchy | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Source credibility | Text only | Color-coded badges |
| Click to read | Links work | Beautiful buttons |
| Mobile friendly | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Statistics | Footer text | Visual cards |
| Engagement | ⭐⭐ | ⭐⭐⭐⭐⭐ |

## Both Formats Generated

The system generates both formats so you can:
- **Read the HTML** for daily consumption (beautiful, engaging)
- **Archive the Markdown** for grep/search/version control
- **Choose based on context** (phone vs desktop, etc.)

## Files Created

```
output/
├── brief.html         # Pretty HTML version (13KB)
├── brief.md          # Plain Markdown version (1KB)
└── archive/
    └── brief_*.md    # Historical briefs
```

## Tips

1. **Bookmark the HTML file** for quick access
2. **Set it as your browser homepage** for automatic viewing
3. **Keep Markdown for searching** old briefs with grep
4. **Share HTML via email** if you want (self-contained file)

Enjoy your beautiful, engaging news briefs! 📰✨
