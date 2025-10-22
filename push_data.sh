#!/bin/bash

# Change to your project directory
cd /home/aces/Bumblebees || exit

# Add all new or modified files
git add -A

# Commit with timestamp message
git commit -m "Auto backup: $(date '+%Y-%m-%d %H:%M:%S') running from crontab" || exit 0

# Push to GitHub
git push 

