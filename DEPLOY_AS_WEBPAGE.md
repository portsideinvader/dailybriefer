# Deploy Your Daily Brief as a Webpage

Your brief is now set up to be automatically published as a webpage!

## 🚀 Quick Setup (5 minutes)

### Step 1: Initialize Git (if not already done)

```bash
cd /Users/sebastianpucher/Tresor/Projects/dailybriefer
git init
git add .
git commit -m "Initial commit - Daily Brief generator"
```

### Step 2: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `dailybriefer` (or your choice)
3. Make it **Public** (required for free GitHub Pages)
4. **Don't** initialize with README (we already have code)
5. Click "Create repository"

### Step 3: Push to GitHub

```bash
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/dailybriefer.git
git branch -M main
git push -u origin main
```

### Step 4: Enable GitHub Pages

1. Go to your repo settings: `https://github.com/YOUR_USERNAME/dailybriefer/settings/pages`
2. Under "Source", select: **Deploy from a branch**
3. Branch: `main`
4. Folder: `/docs`
5. Click **Save**

### Step 5: Run First Generation

The GitHub Action will run daily at 6 AM UTC, but trigger it manually first:

1. Go to: `https://github.com/YOUR_USERNAME/dailybriefer/actions`
2. Click "Generate Daily Brief" workflow
3. Click "Run workflow" → "Run workflow"
4. Wait ~1 minute for completion

### Step 6: Access Your Webpage

Your brief will be live at:
```
https://YOUR_USERNAME.github.io/dailybriefer/
```

**Bookmark this URL on your phone!** 📱

---

## 📱 How It Works

### Daily Updates

- **Automatic**: Runs every day at 6 AM UTC
- **Fresh news**: Fetches latest articles from all 14 sources
- **Auto-publishes**: Updates webpage automatically
- **Zero cost**: Completely free on GitHub

### Manual Updates

You can also generate and push updates manually:

```bash
# Generate brief locally
./generate_brief.sh

# Copy to docs folder
mkdir -p docs
cp output/brief.html docs/index.html
cp output/brief.md docs/brief.md

# Commit and push
git add docs/
git commit -m "Update brief - $(date +'%Y-%m-%d')"
git push
```

The webpage updates in ~30 seconds after pushing.

---

## ⚙️ Customization

### Change Schedule Time

Edit `.github/workflows/daily-brief.yml`:

```yaml
schedule:
  - cron: '0 6 * * *'  # 6 AM UTC
```

**Common times:**
- `'0 6 * * *'` = 6 AM UTC (1 AM EST, 10 PM PST)
- `'0 12 * * *'` = 12 PM UTC (7 AM EST, 4 AM PST)
- `'30 5 * * *'` = 5:30 AM UTC

Use https://crontab.guru to build your schedule.

### Add Custom Domain (Optional)

1. Buy a domain (e.g., `dailybrief.com`)
2. Add DNS CNAME record pointing to `YOUR_USERNAME.github.io`
3. In repo settings → Pages → Custom domain, enter your domain
4. Access at `https://yourdomain.com`

### Private Repository?

GitHub Pages requires **public repos** for free tier.

**Alternative for private:**
- Use Netlify (free tier supports private repos)
- Use Vercel (free tier supports private repos)
- Self-host with simple HTTP server

---

## 📊 What Gets Published

### Files Published to Web:

```
docs/
├── index.html    # Your beautiful sectioned brief
└── brief.md      # Markdown version
```

### What Stays Private:

```
data/
├── articles.db   # Your local article cache
config/
├── feeds.yaml    # Source configuration
```

Only the HTML output is published. Your database and configs stay in the repo but aren't served on the webpage.

---

## 🔧 Troubleshooting

### GitHub Action Fails?

1. Check workflow run: `Actions` tab in GitHub
2. View logs for errors
3. Common issues:
   - RSS feed timeout (retries automatically)
   - Python dependency issue (check requirements.txt)

### Webpage Not Updating?

1. Check if Action ran: `Actions` tab
2. Check if commit was made: `Commits` page
3. GitHub Pages cache: Wait 2-3 minutes
4. Hard refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)

### Want to Test Locally First?

```bash
./generate_brief.sh
./view_brief.sh
```

Verify the brief looks good before pushing.

---

## 🌐 Mobile Access

### Add to Home Screen (iOS)

1. Open `https://YOUR_USERNAME.github.io/dailybriefer/` in Safari
2. Tap Share button (square with arrow)
3. Tap "Add to Home Screen"
4. Name it "Daily Brief"
5. Tap "Add"

Now you have an app icon that opens your brief!

### Add to Home Screen (Android)

1. Open URL in Chrome
2. Tap menu (⋮)
3. Tap "Add to Home screen"
4. Name it and tap "Add"

### Desktop Bookmark

Just bookmark the URL. Check it every morning!

---

## 📈 Benefits of Webpage Deployment

**vs Local File:**
- ✅ Access from any device (phone, tablet, laptop)
- ✅ No need to run script manually
- ✅ Always up-to-date
- ✅ Share with family (if public)

**vs Mobile App:**
- ✅ Much simpler (no app development)
- ✅ Works on iOS and Android
- ✅ No app store submission
- ✅ Instant updates (no app updates)
- ✅ Still $0 cost

**vs Cloud Service:**
- ✅ Still free
- ✅ Still local-first (runs on GitHub's servers)
- ✅ Still private (only HTML published)
- ✅ You own the code and data

---

## 🎯 Your Workflow

### Daily:
1. Wake up
2. Open bookmark/home screen icon
3. Read fresh brief
4. Stay informed!

### Weekly (optional):
1. Check GitHub Action runs to verify it's working
2. Review any failed runs if needed

### As Needed:
1. Update sources in `config/feeds.yaml`
2. Adjust settings in `config/settings.yaml`
3. Push changes to GitHub
4. Next daily run uses new config

---

## 💡 Advanced: Multiple Briefs

You could create different briefs for different topics:

**Example workflow:**
1. Create `config/feeds_tech.yaml` (tech sources only)
2. Modify Action to generate multiple briefs
3. Publish to:
   - `https://you.github.io/dailybriefer/` (main)
   - `https://you.github.io/dailybriefer/tech.html` (tech)
   - `https://you.github.io/dailybriefer/finance.html` (finance only)

---

## 📝 Next Steps

1. Follow "Quick Setup" above
2. Wait for first Action run (or trigger manually)
3. Bookmark your webpage URL
4. Add to phone home screen
5. Enjoy your automated morning brief!

**Your webpage will be:**
- Updated daily at 6 AM
- Beautiful HTML with sections
- Mobile-friendly
- Accessible anywhere
- Still $0 cost
- Still trustworthy (2+ sources)

Welcome to having your own personal news service on the web! 📰🌐
