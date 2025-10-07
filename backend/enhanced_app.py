"""
Enhanced Backend App with Improved Error Handling and Validation
"""
import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, Union
from functools import wraps

from flask import Flask, jsonify, request, g
from flask_cors import CORS
from pydantic import BaseModel, ValidationError
import traceback

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Configuration
class AppConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max request size
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True

app = Flask(__name__)
app.config.from_object(AppConfig)

# Enhanced CORS configuration
CORS(app, 
     origins=os.getenv('ALLOWED_ORIGINS', 
                      'http://localhost:3000,http://127.0.0.1:3000,http://192.168.100.250:3000').split(','),
     supports_credentials=True, 
     allow_headers=['Content-Type', 'Authorization', 'X-User-Email'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# Enhanced logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import after CORS setup
from scraper.scheduler import run_once
from scraper.config import settings
from database.supabase_client import supabase_manager

# Request/Response Models
class ErrorResponse(BaseModel):
    error: str
    code: str
    timestamp: str
    details: Optional[Dict[str, Any]] = None

class SuccessResponse(BaseModel):
    success: bool = True
    data: Optional[Any] = None
    message: Optional[str] = None
    timestamp: str

class SemesterUpdateRequest(BaseModel):
    semesters: list[str]

class LoginRequest(BaseModel):
    email: str

# Rate limiting (simple in-memory implementation)
class RateLimiter:
    def __init__(self, max_requests: int = 100, time_window: int = 3600):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: Dict[str, list] = {}
    
    def is_allowed(self, identifier: str) -> bool:
        now = datetime.now().timestamp()
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Clean old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier] 
            if now - req_time < self.time_window
        ]
        
        if len(self.requests[identifier]) >= self.max_requests:
            return False
        
        self.requests[identifier].append(now)
        return True

rate_limiter = RateLimiter()

# Decorators
def handle_errors(f):
    """Enhanced error handling decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            logger.warning(f"Validation error in {f.__name__}: {e}")
            return jsonify(ErrorResponse(
                error="Validation failed",
                code="VALIDATION_ERROR",
                timestamp=datetime.now().isoformat(),
                details=e.errors()
            ).dict()), 400
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {e}", exc_info=True)
            
            # Don't expose internal errors in production
            if app.debug:
                error_details = {
                    "exception": str(e),
                    "traceback": traceback.format_exc()
                }
            else:
                error_details = None
            
            return jsonify(ErrorResponse(
                error="Internal server error",
                code="INTERNAL_ERROR",
                timestamp=datetime.now().isoformat(),
                details=error_details
            ).dict()), 500
    return decorated_function

def require_user(f):
    """Require authenticated user"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user, error_response, status_code = get_user_from_request()
        if error_response:
            return error_response, status_code
        g.user = user
        return f(*args, **kwargs)
    return decorated_function

def rate_limit(f):
    """Rate limiting decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        
        if not rate_limiter.is_allowed(client_ip):
            return jsonify(ErrorResponse(
                error="Rate limit exceeded",
                code="RATE_LIMIT_EXCEEDED",
                timestamp=datetime.now().isoformat()
            ).dict()), 429
        
        return f(*args, **kwargs)
    return decorated_function

def validate_json(model_class):
    """JSON validation decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify(ErrorResponse(
                    error="Content-Type must be application/json",
                    code="INVALID_CONTENT_TYPE",
                    timestamp=datetime.now().isoformat()
                ).dict()), 400
            
            try:
                validated_data = model_class(**request.json)
                g.validated_data = validated_data
                return f(*args, **kwargs)
            except ValidationError as e:
                return jsonify(ErrorResponse(
                    error="Invalid request data",
                    code="VALIDATION_ERROR",
                    timestamp=datetime.now().isoformat(),
                    details=e.errors()
                ).dict()), 400
        return decorated_function
    return decorator

# Enhanced user management
def get_user_from_request() -> Tuple[Optional[Dict], Optional[Any], Optional[int]]:
    """Extract and validate user from request"""
    user_email = request.headers.get('X-User-Email')
    
    if not user_email:
        if request.is_json:
            user_email = request.json.get('user_email')
    
    if not user_email:
        logger.warning("No user email found in request")
        return None, jsonify(ErrorResponse(
            error="User authentication required",
            code="AUTH_REQUIRED",
            timestamp=datetime.now().isoformat()
        ).dict()), 401
    
    # Validate email format (basic validation)
    if '@' not in user_email or len(user_email) > 254:
        return None, jsonify(ErrorResponse(
            error="Invalid email format",
            code="INVALID_EMAIL",
            timestamp=datetime.now().isoformat()
        ).dict()), 400
    
    try:
        user = supabase_manager.get_or_create_user(user_email)
        logger.info(f"User authenticated: {user['email']}")
        return user, None, None
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        return None, jsonify(ErrorResponse(
            error="User management error",
            code="USER_ERROR",
            timestamp=datetime.now().isoformat()
        ).dict()), 500

# Routes with enhanced error handling
@app.route('/api/health', methods=['GET'])
@handle_errors
@rate_limit
def health_check():
    """Enhanced health check endpoint"""
    health_data = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'environment': os.getenv('ENVIRONMENT', 'development'),
        'checks': {
            'database': True,  # Add actual health checks
            'gmail_api': True,
            'file_system': True
        }
    }
    
    return jsonify(SuccessResponse(
        data=health_data,
        timestamp=datetime.now().isoformat()
    ).dict())

@app.route('/api/config/semesters', methods=['POST'])
@handle_errors
@rate_limit
@require_user
@validate_json(SemesterUpdateRequest)
def update_semesters():
    """Update allowed semesters with validation"""
    data = g.validated_data
    user = g.user
    
    # Additional business logic validation
    if len(data.semesters) > 10:  # Reasonable limit
        return jsonify(ErrorResponse(
            error="Too many semesters selected (max 10)",
            code="SEMESTER_LIMIT_EXCEEDED",
            timestamp=datetime.now().isoformat()
        ).dict()), 400
    
    # Update user settings
    current_settings = supabase_manager.get_user_settings(user['id'])
    current_settings['allowed_semesters'] = data.semesters
    
    success = supabase_manager.save_user_settings(user['id'], current_settings)
    
    if not success:
        return jsonify(ErrorResponse(
            error="Failed to save semester settings",
            code="SAVE_ERROR",
            timestamp=datetime.now().isoformat()
        ).dict()), 500
    
    logger.info(f"Updated semesters for user {user['email']}: {data.semesters}")
    
    return jsonify(SuccessResponse(
        data={'semesters': data.semesters},
        message=f'Updated {len(data.semesters)} semester preferences',
        timestamp=datetime.now().isoformat()
    ).dict())

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify(ErrorResponse(
        error="Endpoint not found",
        code="NOT_FOUND",
        timestamp=datetime.now().isoformat()
    ).dict()), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify(ErrorResponse(
        error="Method not allowed",
        code="METHOD_NOT_ALLOWED",
        timestamp=datetime.now().isoformat()
    ).dict()), 405

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify(ErrorResponse(
        error="Request too large",
        code="REQUEST_TOO_LARGE",
        timestamp=datetime.now().isoformat()
    ).dict()), 413

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Starting enhanced server on 0.0.0.0:{port}")
    print(f"📊 Debug mode: {debug}")
    print(f"🌐 Environment: {os.getenv('ENVIRONMENT', 'development')}")
    
    app.run(host='0.0.0.0', port=port, debug=debug, threaded=True)