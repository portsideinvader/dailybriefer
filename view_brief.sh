#!/bin/bash
# View the latest HTML brief in your default browser

cd "$(dirname "$0")"

if [ -f "output/brief.html" ]; then
    open output/brief.html
    echo "📰 Opening your morning brief in the browser..."
else
    echo "❌ No brief found. Run './generate_brief.sh' first."
    exit 1
fi
