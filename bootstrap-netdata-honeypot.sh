#!/bin/bash
set -euo pipefail

# --------------------------
# CONFIGURATION
# --------------------------
PARENT_IP="172.30.201.214:19999"   # Host Netdata IP + port
API_KEY="bumbleb33"                 # Shared API key for all ephemeral honeypots
NODE_NAME="${HOOD_HOSTNAME:-honeypot}"  # Logical node name (passed from lifecycle script)

# --------------------------
# SET HOSTNAME
# --------------------------
sudo hostnamectl set-hostname "$NODE_NAME"

# --------------------------
# INSTALL NETDATA IF NOT PRESENT
# --------------------------
if ! command -v netdata >/dev/null 2>&1; then
  curl -sSL https://my-netdata.io/kickstart.sh | sudo bash -s -- --dont-wait --disable-telemetry
fi

# --------------------------
# CONFIGURE NETDATA WEB UI (LOCAL ONLY)
# --------------------------
sudo mkdir -p /etc/netdata
sudo tee /etc/netdata/netdata.conf > /dev/null <<NETCONF
[global]
    hostname = $NODE_NAME

[web]
    bind to = 127.0.0.1
    mode = simple
NETCONF

# --------------------------
# CONFIGURE STREAMING TO PARENT
# --------------------------
sudo tee /etc/netdata/stream.conf > /dev/null <<STREAMCONF
[stream]
    enabled = yes

[backend]
    # keep default
STREAMCONF

# Add the API key stanza used by host Netdata
sudo tee /etc/netdata/stream.conf.d/honeypot.stream.conf > /dev/null <<STREAMKEY
[stream]
    enabled = yes
    destination = $PARENT_IP
    api key = $API_KEY
    hostname = $NODE_NAME
STREAMKEY

# --------------------------
# RESTART NETDATA
# --------------------------
sudo systemctl daemon-reload || true
sudo systemctl enable --now netdata
sudo systemctl restart netdata

echo "Netdata installed and streaming as $NODE_NAME -> $PARENT_IP (api key $API_KEY)"

