#!/bin/bash
# Vercel Build Script for Syndicate
# This script runs during the Vercel build process

set -e

echo "Starting Syndicate build for Vercel..."

# Ensure we're in the project root
cd "$(dirname "$0")"

echo "Python version:"
python3 --version

echo "Installing Python dependencies..."
pip install --upgrade pip

# Install only production dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing from requirements.txt..."
    pip install -r requirements.txt
fi

echo "Creating necessary directories..."
mkdir -p /tmp/prometheus
mkdir -p output/charts
mkdir -p output/reports

echo "Vercel build completed successfully!"
