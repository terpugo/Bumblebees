#!/bin/bash

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <channel> <message>"
  exit 1
fi

channel=$1
message=$2

# Sanitize message to remove quotes
message=$(echo "$message" | tr -d '"' | tr -d "'")

# GITIGNORE THIS FILE!!!!! IMPORTANT!!!
url=$(cat /home/aces/Bumblebees/url.env)

# Formats the message properly
get_data_json() {
  cat <<EOF
{ "channel": "$channel", "icon_emoji": ":bot:", "text": "$message" }
EOF
}

# Sends the message to Slack webhook
/usr/bin/curl -X POST -H 'Content-type: application/json; charset=utf-8' --data "$(get_data_json)" $url
