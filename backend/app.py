"""
Flask backend for TimeTable Scraper
Provides RESTful API endpoints for the React frontend
"""
import os
import sys
import json
import logging
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

app = Flask(__name__)
# CORS configuration to allow network access
CORS(app, origins=[
    "http://localhost:3000",
    "http://127.0.0.1:3000", 
    "http://192.168.100.250:3000",  # Your network IP
    "http://192.168.100.250:3000",  # Ensure network IP is allowed
], supports_credentials=True, allow_headers=['Content-Type', 'Authorization'])

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import after CORS setup
from scraper.scheduler import run_once
from scraper.config import settings

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'config_loaded': True
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    try:
        # Don't expose sensitive data
        safe_config = {
            'gmail_query': settings.gmail_query_base,
            'semester_filter': settings.allowed_semesters,
            'schedule_time': f"{settings.check_hour_local:02d}:{settings.check_minute_local:02d}",
            'timezone': settings.tz,
            'max_results': getattr(settings, 'max_results_per_semester', 50)
        }
        return jsonify(safe_config)
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/config/semesters', methods=['POST', 'OPTIONS'])
def update_semesters():
    """Update allowed semesters configuration"""
    # Handle preflight request
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        data = request.get_json()
        if not data or 'semesters' not in data:
            return jsonify({'error': 'Missing semesters data'}), 400
        
        new_semesters = data['semesters']
        if not isinstance(new_semesters, list):
            return jsonify({'error': 'Semesters must be a list'}), 400
        
        # Update the .env file
        env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
        
        # Read current .env content
        env_lines = []
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                env_lines = f.readlines()
        
        # Update or add ALLOWED_SEMESTERS line
        semesters_str = ', '.join(new_semesters)
        updated = False
        
        for i, line in enumerate(env_lines):
            if line.startswith('ALLOWED_SEMESTERS='):
                env_lines[i] = f'ALLOWED_SEMESTERS={semesters_str}\n'
                updated = True
                break
        
        if not updated:
            env_lines.append(f'ALLOWED_SEMESTERS={semesters_str}\n')
        
        # Write back to .env file
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(env_lines)
        
        # Update the current settings object (simple update)
        settings.allowed_semesters = new_semesters
        
        logger.info(f"Updated allowed semesters: {new_semesters}")
        
        return jsonify({
            'success': True,
            'message': f'Updated {len(new_semesters)} allowed semesters',
            'semesters': new_semesters
        })
        
    except Exception as e:
        logger.error(f"Error updating semesters: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/scrape', methods=['POST'])
def scrape_now():
    """Run the scraper once and return results"""
    try:
        logger.info("Starting manual scrape via API")
        result = run_once(show_table=False)
        
        if result and result.get('success'):
            return jsonify({
                'success': True,
                'message': 'Scrape completed successfully',
                'data': result.get('data', []),
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Scrape failed or no data found',
                'error': result.get('error') if result else 'Unknown error',
                'timestamp': datetime.now().isoformat()
            }), 400
            
    except Exception as e:
        logger.error(f"Error during scrape: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/timetable', methods=['GET'])
def get_latest_timetable():
    """Get the latest saved timetable data"""
    try:
        # Check for the latest schedule file
        cache_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'cache')
        
        # Look for schedule files (format: schedule_YYYY-MM-DD.json)
        schedule_files = []
        if os.path.exists(cache_dir):
            for filename in os.listdir(cache_dir):
                if filename.startswith('schedule_') and filename.endswith('.json'):
                    schedule_files.append(filename)
        
        if not schedule_files:
            return jsonify({
                'success': False,
                'message': 'No cached schedule data found. Run a scrape first.',
                'timestamp': datetime.now().isoformat()
            }), 404
        
        # Get the most recent schedule file
        latest_file = max(schedule_files)
        schedule_file = os.path.join(cache_dir, latest_file)
        
        with open(schedule_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return jsonify({
                'success': True,
                'data': data,
                'timestamp': datetime.now().isoformat(),
                'cached': True,
                'source_file': latest_file
            })
            
    except Exception as e:
        logger.error(f"Error reading cached data: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current system status"""
    try:
        # Check if cache file exists and when it was last updated
        cache_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'cache', 'last_checked.json')
        
        status = {
            'timestamp': datetime.now().isoformat(),
            'cache_exists': os.path.exists(cache_file),
            'last_update': None
        }
        
        if os.path.exists(cache_file):
            stat = os.stat(cache_file)
            status['last_update'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting server on 0.0.0.0:{port}")
    print(f"Access URLs:")
    print(f"  Local: http://localhost:{port}")
    print(f"  Network: http://192.168.100.250:{port}")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)