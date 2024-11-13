#!/bin/bash

# Change to the directory of this script (the .sh file location)
cd "$(dirname "$0")"

# Run the Python script
python3 src/maze-game.py

# Pause to display the script's output before closing (press Enter to continue)
read -p "Press Enter to continue..."
