"""
Flask Application Factory
"""
import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, jsonify
from dotenv import load_dotenv

from app.config import config
from app.extensions import db, migrate, jwt, cors, limiter, swagger


def create_app(config_name=None):
    """
    Create and configure Flask application.
    
    Args:
        config_name (str): Configuration name ('development', 'production', 'testing')
        
    Returns:
        Flask: Configured Flask application
    """
    # Load environment variables
    load_dotenv()
    
    # Determine config
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Import models to ensure they are registered with SQLAlchemy
    from app.models import Admin, Employee
    
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, origins=app.config['CORS_ORIGINS'])
    limiter.init_app(app)
    
    # Configure Swagger
    swagger.init_app(app)
    
    # Configure JWT callbacks
    configure_jwt_callbacks(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Configure error handlers
    configure_error_handlers(app)
    
    # Configure logging
    configure_logging(app)
    
    # Create upload directories
    create_directories(app)
    
    return app


def register_blueprints(app):
    """Register Flask blueprints."""
    from app.routes.auth import auth_bp
    from app.routes.employees import employees_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(employees_bp, url_prefix='/api/employees')
    
    # Root route
    @app.route('/')
    def index():
        return jsonify({
            'message': 'PRODIGY INFOTEC Employee Management System API',
            'version': '1.0.0',
            'status': 'active',
            'docs': '/api/docs/'
        })
    
    # Health check route
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy', 'service': 'Employee Management System'})


def configure_error_handlers(app):
    """Configure error handlers."""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad Request',
            'message': 'The request was invalid or malformed.',
            'status_code': 400
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication is required to access this resource.',
            'status_code': 401
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource.',
            'status_code': 403
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found.',
            'status_code': 404
        }), 404
    
    @app.errorhandler(429)
    def ratelimit_handler(error):
        return jsonify({
            'error': 'Too Many Requests',
            'message': 'Rate limit exceeded. Please try again later.',
            'status_code': 429
        }), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred.',
            'status_code': 500
        }), 500


def configure_logging(app):
    """Configure application logging."""
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Set up file handler
    file_handler = RotatingFileHandler(
        'logs/app.log', 
        maxBytes=10240000,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))
    
    app.logger.addHandler(file_handler)
    app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))
    app.logger.info('Employee Management System startup')


def configure_jwt_callbacks(app):
    """Configure JWT callbacks."""
    # Import revoked tokens from auth routes
    from app.routes.auth import revoked_tokens
    
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        """Check if token is revoked."""
        return jwt_payload['jti'] in revoked_tokens


def create_directories(app):
    """Create necessary directories."""
    upload_dir = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
        os.makedirs(os.path.join(upload_dir, 'profiles'))
    
    if not os.path.exists('logs'):
        os.makedirs('logs')
