"""
Security Utilities
"""
from functools import wraps
from flask import jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.admin import Admin


def admin_required(f):
    """
    Decorator to require admin authentication.
    
    Usage:
        @admin_required
        def protected_route():
            pass
    """
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        try:
            admin_id = get_jwt_identity()
            admin = Admin.query.filter_by(id=int(admin_id), is_active=True).first()
            
            if not admin:
                return jsonify({
                    'error': 'Unauthorized',
                    'message': 'Admin account not found or inactive.'
                }), 401
            
            return f(admin, *args, **kwargs)
        
        except Exception as e:
            current_app.logger.error(f'Authentication error: {str(e)}')
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Authentication failed.'
            }), 401
    
    return decorated_function


def get_current_admin():
    """
    Get the current authenticated admin.
    
    Returns:
        Admin: Current admin object or None
    """
    try:
        admin_id = get_jwt_identity()
        if admin_id:
            return Admin.query.filter_by(id=int(admin_id), is_active=True).first()
        return None
    except Exception:
        return None


def validate_admin_credentials(username_or_email, password):
    """
    Validate admin credentials.
    
    Args:
        username_or_email (str): Username or email
        password (str): Password
        
    Returns:
        tuple: (admin_object, is_valid)
    """
    if not username_or_email or not password:
        return None, False
    
    # Try to find admin by username or email
    admin = Admin.query.filter(
        (Admin.username == username_or_email) | 
        (Admin.email == username_or_email)
    ).filter_by(is_active=True).first()
    
    if admin and admin.check_password(password):
        return admin, True
    
    return None, False