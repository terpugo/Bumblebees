#!/bin/bash
/home/aces/Bumblebees/slack.sh C09MYJC3M4N "$(date): auto pushing to github"
set -euo pipefail

# LOG file for debugging
LOG="/home/aces/Bumblebees/push_data.log"

# make sure all stdout/stderr goes to the logfile
exec >>"$LOG" 2>&1

echo "=== START $(date -u +"%Y-%m-%d %H:%M:%SZ") ==="

# Minimal PATH so cron can find binaries
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export HOME="/home/aces"

# Repo info
REPO_DIR="/home/aces/Bumblebees"
PYTHON="/usr/bin/python3"
GIT="/usr/bin/git"
BRANCH="main"

# Optional: force git to use a specific identity file (edit path to your key)
# Only use if you have a key without passphrase or a deploy key
#export GIT_SSH_COMMAND="ssh -i /home/aces/.ssh/id_ed25519 -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes"

echo "Using PATH=$PATH"
echo "Using HOME=$HOME"
echo "Repo dir: $REPO_DIR"

# Run the processor (keep errors from aborting the rest, if you prefer)
cd "$REPO_DIR" || { echo "ERROR: cannot cd to $REPO_DIR"; exit 1; }

# Run daily_processor (script must be executable or invoke python explicitly)
# Using explicit python path prevents "command not found" issues
$PYTHON "$REPO_DIR/daily_processor.py" "$REPO_DIR/Attacker_Data" || echo "Processor returned non-zero"

# Git operations
$GIT add -A

# If nothing staged, exit quietly
if $GIT diff --staged --quiet; then
  echo "Nothing to commit."
  echo "=== END $(date -u +"%Y-%m-%d %H:%M:%SZ") ==="
  exit 0
fi

COMMIT_MSG="Auto backup: $(date '+%Y-%m-%d %H:%M:%S') running from crontab"
# commit (|| true to avoid non-zero exit from cron if we still want to continue)
$GIT commit -m "$COMMIT_MSG" || { echo "git commit failed"; exit 0; }

# push (GIT_SSH_COMMAND env will be used)
$GIT push origin "$BRANCH" || { echo "git push failed"; exit 1; }

echo "Pushed successfully: $COMMIT_MSG"
echo "=== END $(date -u +"%Y-%m-%d %H:%M:%SZ") ==="

