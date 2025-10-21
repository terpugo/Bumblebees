#!/bin/bash

# Change to your project directory
cd /home/aces/Bumblebees/honeypot_data_sheets || exit

# Add all new or modified files
git add .

# Commit with timestamp message
git commit -m "Auto backup: $(date '+%Y-%m-%d %H:%M:%S')" || exit 0

# Push to GitHub
git push 

