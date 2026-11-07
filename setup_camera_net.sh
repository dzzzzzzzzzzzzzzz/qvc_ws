#!/bin/bash

# Configuration parameters
INTERFACE="enp5s0"
IP_ADDRESS="192.168.1.100/24"
MTU_SIZE="9000"
CONNECTION_NAME="Wired connection 1"

echo "--- Setting up GigE Camera Network ---"

# 1. Use nmcli to set static IP and MTU
# Modify the connection parameters
sudo nmcli connection modify "$CONNECTION_NAME" \
    ipv4.method manual \
    ipv4.addresses "$IP_ADDRESS" \
    802-3-ethernet.mtu "$MTU_SIZE"

# 2. Restart the connection to apply settings
echo "Restarting network connection: $CONNECTION_NAME"
sudo nmcli connection down "$CONNECTION_NAME"
sudo nmcli connection up "$CONNECTION_NAME"

# 3. Verify MTU and IP
echo "--- Current Network Status ---"
ip link show "$INTERFACE" | grep mtu
ip addr show "$INTERFACE" | grep inet

echo "Network setup complete! You can now run the Python camera script."
