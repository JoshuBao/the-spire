#!/bin/bash
# Quick launcher for The Spire

# Check if dependencies are installed
if ! python -c "import rich; import textual" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -q -r requirements.txt
fi

# Run the game
python main.py
