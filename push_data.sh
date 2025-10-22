#!/bin/bash

/usr/bin/python3 /home/aces/Bumblebees/daily_processor.py --date "$(date +%F)" /home/aces/Bumblebees/Attacker_Data
# Change to your project directory
cd /home/aces/Bumblebees || exit

# Add all new or modified files
git add -A

# Commit with timestamp message
git commit -m "Auto backup: $(date '+%Y-%m-%d %H:%M:%S') running from crontab" || exit 0

# Push to GitHub
git push 

