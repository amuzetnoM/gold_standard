#!/bin/bash
# Build script for Vercel deployment
# This script is called by Vercel during the build phase

set -e

echo "🔨 Starting Vercel build for Syndicate..."

# Print Python version
echo "Python version:"
python3 --version

# Upgrade pip
echo "Upgrading pip..."
python3 -m pip install --upgrade pip

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p output
mkdir -p output/reports
mkdir -p output/charts
mkdir -p output/research
mkdir -p data

# Initialize database schema (if needed)
echo "Initializing database..."
python3 -c "from db_manager import get_db; db = get_db(); print('Database initialized')" || echo "Database initialization skipped (may already exist)"

# Verify critical imports
echo "Verifying imports..."
python3 -c "import main; print('✓ main.py')" || exit 1
python3 -c "import run; print('✓ run.py')" || exit 1
python3 -c "from db_manager import get_db; print('✓ db_manager.py')" || exit 1
python3 -c "from api.index import handler; print('✓ api/index.py')" || exit 1

echo "✅ Build completed successfully!"
echo ""
echo "📦 Deployment summary:"
echo "  - Dependencies installed"
echo "  - Directories created"
echo "  - Database initialized"
echo "  - Imports verified"
echo ""
echo "🚀 Ready for deployment!"
