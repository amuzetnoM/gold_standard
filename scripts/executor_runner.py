#!/usr/bin/env python3
"""Simple executor runner: repeatedly runs executor_daemon.py --once
with configurable sleep/backoff. Intended as a lightweight supervisor when
systemd or other process manager isn't used.
"""
import os
import time
import subprocess
import sys

MAX_TASKS = int(os.getenv("EXECUTOR_MAX_TASKS", "50"))
SLEEP_NO_WORK = int(os.getenv("EXECUTOR_SLEEP_NO_WORK", "60"))
SLEEP_ON_ERROR = int(os.getenv("EXECUTOR_SLEEP_ON_ERROR", "10"))

def run_once():
    cmd = f"set -a && source .env && set +a && {sys.executable} scripts/executor_daemon.py --once --max-tasks {MAX_TASKS}"
    try:
        res = subprocess.run(cmd, shell=True)
        return res.returncode
    except Exception as e:
        print("Executor runner error:", e)
        return 2

if __name__ == '__main__':
    print("Executor runner starting. CTRL+C to stop.")
    while True:
        rc = run_once()
        if rc == 0:
            # No error; sleep then continue
            time.sleep(SLEEP_NO_WORK)
        else:
            # Error; short sleep then retry
            time.sleep(SLEEP_ON_ERROR)
