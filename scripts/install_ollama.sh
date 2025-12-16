#!/usr/bin/env bash
set -euo pipefail

# Install Ollama (Linux x86_64 assumed)
# Usage: sudo ./install_ollama.sh

OLLAMA_MODEL=${OLLAMA_MODEL:-"llama3.2"}
OLLAMA_BIN=${OLLAMA_BIN:-/usr/local/bin/ollama}

echo "[OLLAMA] Installing Ollama..."

if command -v ollama >/dev/null 2>&1; then
  echo "[OLLAMA] ollama already installed at $(command -v ollama)"
else
  # Download official linux package (stable) - prefer .deb if apt/dpkg available
  if command -v apt >/dev/null 2>&1 && command -v dpkg >/dev/null 2>&1; then
    tmpdeb=$(mktemp -p /tmp ollama-XXXXXX.deb)
    echo "[OLLAMA] Downloading .deb..."
    if ! curl -fsSL -o "$tmpdeb" "https://ollama.com/download/ollama-linux-amd64.deb"; then
      echo "[OLLAMA] .deb not found, trying generic installer"
      curl -fsSL https://ollama.com/install.sh | sudo bash || { echo "[OLLAMA] Generic installer failed"; exit 1; }
    else
      echo "[OLLAMA] Installing .deb (requires sudo)..."
      if ! sudo dpkg -i "$tmpdeb"; then
        echo "[OLLAMA] dpkg install failed, trying generic installer"
        curl -fsSL https://ollama.com/install.sh | sudo bash || { echo "[OLLAMA] Generic installer failed"; exit 1; }
      fi
      rm -f "$tmpdeb"
    fi
  fi
fi

# Ensure service/daemon is running (if suitable on this distro)
if command -v ollama >/dev/null 2>&1; then
  echo "[OLLAMA] ollama installed: $(ollama --version 2>/dev/null || echo 'version unknown')"
else
  echo "[OLLAMA] Installation did not produce an ollama binary. Please check installer output." >&2
  exit 2
fi

# Start Ollama served daemon (if not running)
if curl -sSf "http://localhost:11434/api/tags" >/dev/null 2>&1; then
  echo "[OLLAMA] ollama daemon appears to be running"
else
  echo "[OLLAMA] Starting ollama daemon"
  sudo systemctl enable --now ollama || {
    echo "[OLLAMA] systemd unit not available; starting via 'ollama serve' in background"
    nohup ollama serve >/var/log/ollama_serve.log 2>&1 &
    sleep 2
  }
fi

# Pull requested model
if [[ -n "$OLLAMA_MODEL" ]]; then
  echo "[OLLAMA] Pulling model: $OLLAMA_MODEL"
  if ollama pull "$OLLAMA_MODEL"; then
    echo "[OLLAMA] Model pulled: $OLLAMA_MODEL"
  else
    echo "[OLLAMA] Failed to pull model $OLLAMA_MODEL (check connectivity and available models)" >&2
  fi
fi

echo "[OLLAMA] Install script finished. Verify with: ollama list"