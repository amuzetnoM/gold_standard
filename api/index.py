#!/usr/bin/env python3
"""
Vercel Serverless Entry Point for Syndicate
Provides HTTP interface and background task execution for autonomous operation.
"""
import json
import os
import sys
import threading
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Global state for background worker
_background_worker_started = False
_background_worker_lock = threading.Lock()


def start_background_worker():
    """
    Start the autonomous analysis worker in the background.
    This ensures continuous operation even on serverless platforms.
    """
    global _background_worker_started
    
    with _background_worker_lock:
        if _background_worker_started:
            return
        _background_worker_started = True
    
    def worker():
        """Background worker that runs continuous analysis."""
        try:
            # Import inside worker to avoid module loading issues
            from main import Config, setup_logging, create_llm_provider, execute
            import run
            
            # Set up configuration
            config = Config()
            logger = setup_logging(config)
            
            # Create LLM provider
            model = create_llm_provider(config, logger)
            
            logger.info("[VERCEL] Starting autonomous background worker")
            
            # Run in continuous loop with proper error handling
            while True:
                try:
                    # Run analysis cycle
                    logger.info(f"[VERCEL] Running analysis cycle at {datetime.now()}")
                    success = execute(config, logger, model=model, dry_run=False, no_ai=False, force=False)
                    
                    if success:
                        # Run post-analysis tasks with wait-forever to ensure completion
                        try:
                            run._run_post_analysis_tasks(
                                force_inline=True,
                                wait_for_completion=False,
                                wait_forever=True
                            )
                        except Exception as e:
                            logger.error(f"[VERCEL] Post-analysis tasks error: {e}")
                    
                    # Sleep for interval (default: 4 hours = 240 minutes)
                    interval_minutes = int(os.getenv('RUN_INTERVAL_MINUTES', '240'))
                    logger.info(f"[VERCEL] Next cycle in {interval_minutes} minutes")
                    time.sleep(interval_minutes * 60)
                    
                except Exception as e:
                    logger.error(f"[VERCEL] Worker cycle error: {e}", exc_info=True)
                    # Sleep for 5 minutes on error before retry
                    time.sleep(300)
                    
        except Exception as e:
            print(f"[VERCEL] Fatal worker error: {e}")
            sys.stderr.write(f"[VERCEL] Fatal worker error: {e}\n")
    
    # Start worker thread as daemon
    worker_thread = threading.Thread(target=worker, daemon=True)
    worker_thread.start()
    print("[VERCEL] Background worker thread started")


class handler(BaseHTTPRequestHandler):
    """
    Vercel serverless function handler.
    Provides health checks and status endpoints while running continuous background tasks.
    """
    
    def do_GET(self):
        """Handle GET requests."""
        try:
            # Start background worker on first request
            start_background_worker()
            
            # Parse path
            path = self.path.split('?')[0]
            
            if path == '/' or path == '/health':
                self.send_health_check()
            elif path == '/status':
                self.send_status()
            elif path == '/api/health':
                self.send_health_check()
            elif path == '/api/status':
                self.send_status()
            else:
                self.send_not_found()
                
        except Exception as e:
            self.send_error_response(str(e))
    
    def do_POST(self):
        """Handle POST requests."""
        try:
            # Start background worker on first request
            start_background_worker()
            
            path = self.path.split('?')[0]
            
            if path == '/api/trigger':
                self.trigger_analysis()
            else:
                self.send_not_found()
                
        except Exception as e:
            self.send_error_response(str(e))
    
    def send_health_check(self):
        """Send health check response."""
        try:
            # Quick health check
            from db_manager import get_db
            db = get_db()
            health = db.get_system_health()
            
            response = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'service': 'syndicate',
                'version': '3.7.0',
                'background_worker': 'running' if _background_worker_started else 'not_started',
                'health': health
            }
            
            self.send_json_response(response, 200)
            
        except Exception as e:
            self.send_json_response({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, 500)
    
    def send_status(self):
        """Send detailed status response."""
        try:
            from db_manager import get_db
            db = get_db()
            
            # Get comprehensive status
            health = db.get_system_health()
            stats = db.get_statistics()
            
            response = {
                'status': 'ok',
                'timestamp': datetime.now().isoformat(),
                'service': 'syndicate',
                'version': '3.7.0',
                'background_worker': 'running' if _background_worker_started else 'not_started',
                'statistics': stats,
                'health': health,
                'environment': {
                    'python_version': sys.version,
                    'platform': sys.platform,
                    'interval_minutes': os.getenv('RUN_INTERVAL_MINUTES', '240')
                }
            }
            
            self.send_json_response(response, 200)
            
        except Exception as e:
            self.send_error_response(str(e))
    
    def trigger_analysis(self):
        """Manually trigger an analysis cycle."""
        try:
            from main import Config, setup_logging, create_llm_provider, execute
            import run
            
            config = Config()
            logger = setup_logging(config)
            model = create_llm_provider(config, logger)
            
            # Run analysis
            success = execute(config, logger, model=model, dry_run=False, no_ai=False, force=False)
            
            if success:
                # Run post-analysis tasks
                run._run_post_analysis_tasks(
                    force_inline=True,
                    wait_for_completion=True,
                    max_wait_seconds=60
                )
            
            response = {
                'status': 'success' if success else 'failed',
                'timestamp': datetime.now().isoformat(),
                'message': 'Analysis cycle completed' if success else 'Analysis cycle failed'
            }
            
            self.send_json_response(response, 200 if success else 500)
            
        except Exception as e:
            self.send_error_response(str(e))
    
    def send_json_response(self, data, status_code=200):
        """Send JSON response."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def send_error_response(self, error_message, status_code=500):
        """Send error response."""
        response = {
            'status': 'error',
            'error': error_message,
            'timestamp': datetime.now().isoformat()
        }
        self.send_json_response(response, status_code)
    
    def send_not_found(self):
        """Send 404 response."""
        response = {
            'status': 'error',
            'error': 'Not Found',
            'path': self.path,
            'timestamp': datetime.now().isoformat()
        }
        self.send_json_response(response, 404)


# For local testing
if __name__ == '__main__':
    from http.server import HTTPServer
    
    port = int(os.getenv('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), handler)
    print(f"[VERCEL] Starting test server on port {port}")
    print(f"[VERCEL] Health check: http://localhost:{port}/health")
    print(f"[VERCEL] Status: http://localhost:{port}/status")
    server.serve_forever()
