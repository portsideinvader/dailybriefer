# Filtering Rules & How to See More Financial News

## Current Rules (Why WSJ Isn't Showing)

### The Pipeline:
```
569 articles fetched
    ↓
90 recent (last 24h)
    ↓
Clustering by title similarity
    ↓
62 clusters found
    ↓
❌ FILTER: Keep only 2+ sources
    ↓
4 events remain
```

### Problem: Multi-Source Requirement

**Current Rule:**
- `min_sources_per_event: 2`
- Events need 2+ different sources

**Why Financial News Gets Filtered:**
- WSJ: "Tesla stock drops 10% on earnings miss"
- Bloomberg: (covering different company)
- FT: (covering different angle)
- Result: Only 1 source → **FILTERED OUT**

**Why General News Shows Up:**
- BBC: "Israel approves 19 settlements"
- Guardian: "Israel approves 19 settlements"
- FT: "Israel approves 19 settlements"
- Result: 3 sources → **SHOWS UP**

---

## 🎯 Solutions (3 Options)

### Option 1: Lower Multi-Source Requirement (EASIEST) ⭐

**Change:** Allow single-source financial stories
**How:** Create a separate category for "verified" vs "developing" stories

**Edit `config/settings.yaml`:**
```yaml
min_sources_per_event: 1  # Was 2
```

**Result:**
- You'll see WSJ-only business stories
- But ALSO single-source general news
- More noise, less verification

**Pros:**
- ✅ See all financial news immediately
- ✅ Simple change

**Cons:**
- ❌ Less trustworthy (single source)
- ❌ More clutter in brief

---

### Option 2: Create Separate Financial Brief (RECOMMENDED) ⭐⭐⭐

**Change:** Two briefs - "Verified News" (2+ sources) + "Financial Watch" (1 source OK)

**How:** Add configuration for topic-specific briefs

**Edit `config/settings.yaml`:**
```yaml
# Main brief settings
min_sources_per_event: 2

# Financial-only brief (relaxed rules)
financial_brief:
  enabled: true
  min_sources_per_event: 1
  financial_sources_only: ['wsj_world', 'wsj_business', 'bloomberg',
                          'ft_world', 'cnbc_top', 'marketwatch']
  max_events: 10
```

**Result:**
- `output/brief.html` - Verified multi-source news (current quality)
- `output/financial.html` - Financial stories (relaxed rules)

**Pros:**
- ✅ Best of both worlds
- ✅ Keep verification for general news
- ✅ See all financial stories
- ✅ Clear separation

**Cons:**
- ⚠️ Requires code changes (I can implement)

---

### Option 3: Lower Similarity Threshold (TARGETED) ⭐⭐

**Change:** Make clustering more aggressive to catch similar financial stories

**Edit `config/settings.yaml`:**
```yaml
similarity_threshold: 0.25  # Was 0.35
```

**How it helps:**
```
Before (0.35):
  WSJ: "Tesla Q4 earnings disappoint investors"
  Bloomberg: "Elon Musk's Tesla misses revenue targets"
  → Similarity: 0.30 → NOT CLUSTERED (different words)

After (0.25):
  WSJ: "Tesla Q4 earnings disappoint investors"
  Bloomberg: "Elon Musk's Tesla misses revenue targets"
  → Similarity: 0.30 → CLUSTERED! (same topic)
```

**Result:**
- Financial sources more likely to cluster together
- "Tesla earnings" story would group WSJ + Bloomberg + FT

**Pros:**
- ✅ Better financial story clustering
- ✅ Still requires 2+ sources
- ✅ Maintains verification

**Cons:**
- ⚠️ May group unrelated stories (over-clustering)
- ⚠️ Still misses truly unique WSJ stories

---

## 📊 My Recommendation: Option 2 (Two Briefs)

### Implementation Plan:

**Morning Brief (Verified):**
- 2+ sources required
- General + Financial news
- High trust, low noise
- Example: "Israel settlements" (Guardian, FT, BBC)

**Financial Watch (Comprehensive):**
- 1 source OK
- Financial sources only
- Timely business news
- Example: "Apple earnings beat" (WSJ only)

### What You'd See Each Morning:

```
output/
├── brief.html          # Your main verified news (current quality)
├── financial.html      # Comprehensive financial news (new)
└── brief.md           # Markdown version
```

**Quick workflow:**
```bash
./generate_brief.sh
# Generates both

./view_brief.sh
# Opens main brief

open output/financial.html
# Opens financial brief
```

---

## 🔧 Quick Fix For Now: Lower to 1 Source

If you want to see WSJ immediately:

**Edit `config/settings.yaml`:**
```yaml
min_sources_per_event: 1  # Change from 2
```

**Run:**
```bash
./generate_brief.sh
```

**You'll see:**
- 15-20 events instead of 4
- All WSJ business stories
- All Bloomberg exclusives
- All FT unique coverage
- Plus all the general news

**Trade-off:**
- ❌ Less verification
- ❌ More articles to read through
- ✅ Won't miss financial news

---

## 📈 Real Example Comparison

### Current (2+ sources):
```
Event #1: Israel settlements
  Sources: Guardian, FT, BBC (3)

Event #2: Venezuela tanker
  Sources: BBC, FT, NYT (3)

Event #3: Trump-Epstein files
  Sources: FT, Guardian (2)

Event #4: South Africa shooting
  Sources: NYT, NPR (2)
```

### With 1 source allowed:
```
Event #1: Israel settlements
  Sources: Guardian, FT, BBC (3)

Event #2: Venezuela tanker
  Sources: BBC, FT, NYT (3)

Event #3: Apple stock jumps 5% ✨ NEW
  Sources: WSJ (1)

Event #4: Fed signals rate cut ✨ NEW
  Sources: Bloomberg (1)

Event #5: Tech layoffs continue ✨ NEW
  Sources: CNBC (1)

... (15 more events)
```

---

## 🎯 What Would You Like?

**Choose your preference:**

### A) Quick Fix (5 seconds)
Lower `min_sources_per_event: 1`
→ See everything, less verification

### B) Smart Solution (I implement)
Create separate financial brief
→ Best of both worlds

### C) Middle Ground
Lower `similarity_threshold: 0.25`
→ Better clustering, keep verification

### D) Current System
Keep as-is, only see multi-source stories
→ Maximum trust, miss some financial news

---

## Current Stats

**What you're seeing now:**
- 90 articles in last 24h
- 62 clusters found
- 4 events (2+ sources each)
- 96% filtered out

**What you'd see with min_sources=1:**
- 90 articles in last 24h
- 62 clusters found
- ~20 events (1+ sources each)
- 78% filtered out
- More WSJ, Bloomberg, FT unique stories

**What you'd see with separate financial brief:**
- Main: 4 verified events (current quality)
- Financial: 10-15 business stories (relaxed rules)
- Total: ~19 events across two briefs
