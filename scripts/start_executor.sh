#!/usr/bin/env bash
# Lightweight runner script for containerized gold_standard executor
set -euo pipefail
cd /opt/gold_standard
# Start optional metrics server in background
python3 scripts/metrics_server.py &
# Run executor daemon in drain mode once
python3 scripts/executor_daemon.py --once
