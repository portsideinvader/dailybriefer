#!/bin/bash
# Daily Briefer - Quick run script

set -e

# Change to script directory
cd "$(dirname "$0")"

# Run the brief generator
python3 -m src.main

# Display success message
echo ""
echo "=========================================="
echo "📰 Your morning brief is ready!"
echo "=========================================="
echo ""
echo "View formats:"
echo "  HTML (recommended): ./view_brief.sh"
echo "  or open: output/brief.html"
echo ""
echo "  Markdown: cat output/brief.md"
echo "=========================================="
echo ""
