#!/bin/bash
set -e

SYNDICATE_ROOT="/home/ali_shakil_backup_gmail_com/syndicate"
SYSTEMD_DIR="/etc/systemd/system"

echo "Copying normalized systemd files..."
sudo cp $SYNDICATE_ROOT/deploy/systemd/normalized/syndicate-*.{service,timer} $SYSTEMD_DIR/

echo "Fixing permissions..."
sudo chown root:root $SYSTEMD_DIR/syndicate-*
sudo chmod 644 $SYSTEMD_DIR/syndicate-*

echo "Reloading systemd..."
sudo systemctl daemon-reload

echo "Enabling services and timers..."
sudo systemctl enable syndicate-daemon.service
sudo systemctl enable syndicate-discord.service
sudo systemctl enable syndicate-executor.service
sudo systemctl enable syndicate-cleanup.timer
sudo systemctl enable syndicate-health.timer
sudo systemctl enable syndicate-publish.timer

echo "Starting services and timers..."
sudo systemctl start syndicate-daemon.service
sudo systemctl start syndicate-discord.service
sudo systemctl start syndicate-executor.service
sudo systemctl start syndicate-cleanup.timer
sudo systemctl start syndicate-health.timer
sudo systemctl start syndicate-publish.timer

echo "Deployment complete."
sudo systemctl status syndicate-daemon.service --no-pager
