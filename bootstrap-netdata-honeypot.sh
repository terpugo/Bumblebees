#!/bin/bash
# Bootstrap Netdata for ephemeral honeypot container

# -----------------------
# CONFIGURATION
# -----------------------
HOST_IP="172.30.201.214"       # Host Netdata IP
HOST_PORT="19999"              # Host Netdata port (default 19999)
API_KEY="bumbleb33"            # Shared API key
NODE_NAME="${HOOD_HOSTNAME:-$(hostname)}"  # Container hostname for Netdata

# -----------------------
# CREATE STREAM CONFIG
# -----------------------
sudo tee /etc/netdata/stream.conf > /dev/null <<EOF
[stream]
    enabled = yes

[backend]
    enabled = yes
    type = proxy
    destination = ${HOST_IP}:${HOST_PORT}
    api key = ${API_KEY}
    hostname = ${NODE_NAME}
EOF

# -----------------------
# RESTART NETDATA
# -----------------------
sudo systemctl restart netdata

# -----------------------
# FORCE NODE REGISTRATION
# -----------------------
# This ensures streaming starts immediately
if [ -f /usr/libexec/netdata/netdata-claim.sh ]; then
    sudo /usr/libexec/netdata/netdata-claim.sh -o
fi

echo "Bootstrap complete: Netdata streaming configured to ${HOST_IP}:${HOST_PORT} as node '${NODE_NAME}'."

