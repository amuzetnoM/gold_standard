#!/usr/bin/env python3
"""
Vercel Serverless Function Entry Point for Syndicate Web UI
This adapts the Flask application to work with Vercel's serverless architecture.

Note: This is a WSGI adapter for Vercel's Python runtime.
Flask-SocketIO real-time features will fallback to long-polling in serverless.
"""
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Set default environment variables for Vercel
os.environ.setdefault("WEB_UI_HOST", "0.0.0.0")
os.environ.setdefault("WEB_UI_PORT", "5000")
os.environ.setdefault("FLASK_ENV", "production")
os.environ.setdefault("FLASK_DEBUG", "false")

# Import the Flask app (not socketio.run, just the app)
from web_ui.app import app

# Vercel expects a WSGI application
# The app object is already a Flask WSGI app
# Vercel's Python runtime will handle the WSGI interface
application = app

# For backwards compatibility
handler = app

