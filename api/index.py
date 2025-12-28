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


def handler(request):
    """
    Vercel serverless function handler.
    Compatible with Vercel's Python runtime.
    """
    # Start background worker on first request
    start_background_worker()
    
    # Get request details
    path = request.get('path', '/')
    method = request.get('method', 'GET')
    
    try:
        if method == 'GET':
            if path in ['/', '/health', '/api/health']:
                return handle_health()
            elif path in ['/status', '/api/status']:
                return handle_status()
            else:
                return handle_not_found(path)
        elif method == 'POST':
            if path == '/api/trigger':
                return handle_trigger()
            else:
                return handle_not_found(path)
        else:
            return {
                'statusCode': 405,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'status': 'error',
                    'error': 'Method Not Allowed',
                    'timestamp': datetime.now().isoformat()
                })
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
        }


def handle_health():
    """Handle health check requests."""
    try:
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
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
        }


def handle_status():
    """Handle status requests."""
    try:
        from db_manager import get_db
        db = get_db()
        
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
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
        }


def handle_trigger():
    """Handle manual trigger requests."""
    try:
        from main import Config, setup_logging, create_llm_provider, execute
        import run
        
        config = Config()
        logger = setup_logging(config)
        model = create_llm_provider(config, logger)
        
        # Run analysis
        success = execute(config, logger, model=model, dry_run=False, no_ai=False, force=False)
        
        if success:
            # Run post-analysis tasks with timeout
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
        
        return {
            'statusCode': 200 if success else 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
        }


def handle_not_found(path):
    """Handle 404 responses."""
    return {
        'statusCode': 404,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'status': 'error',
            'error': 'Not Found',
            'path': path,
            'timestamp': datetime.now().isoformat()
        })
    }


# For local testing with HTTP server
if __name__ == '__main__':
    from http.server import HTTPServer, BaseHTTPRequestHandler
    
    class LocalHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            result = handler({'path': self.path, 'method': 'GET'})
            self.send_response(result['statusCode'])
            for key, value in result.get('headers', {}).items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(result['body'].encode())
        
        def do_POST(self):
            result = handler({'path': self.path, 'method': 'POST'})
            self.send_response(result['statusCode'])
            for key, value in result.get('headers', {}).items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(result['body'].encode())
    
    port = int(os.getenv('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), LocalHandler)
    print(f"[VERCEL] Starting test server on port {port}")
    print(f"[VERCEL] Health check: http://localhost:{port}/health")
    print(f"[VERCEL] Status: http://localhost:{port}/status")
    server.serve_forever()
