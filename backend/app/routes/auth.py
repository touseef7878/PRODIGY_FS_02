"""
Authentication Routes
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from flasgger import swag_from

from app.extensions import db, limiter
from app.utils.security import validate_admin_credentials, get_current_admin
from app.models.admin import Admin

auth_bp = Blueprint('auth', __name__)

# Store revoked tokens in memory (use Redis in production)
revoked_tokens = set()


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """
    Admin Login
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: credentials
        description: Login credentials
        required: true
        schema:
          type: object
          required:
            - username_or_email
            - password
          properties:
            username_or_email:
              type: string
              description: Username or email address
              example: admin
            password:
              type: string
              description: Password
              example: ProdigyAdmin2024!
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            message:
              type: string
              example: Login successful
            admin:
              type: object
              properties:
                id:
                  type: integer
                username:
                  type: string
                email:
                  type: string
                is_active:
                  type: boolean
            access_token:
              type: string
              description: JWT access token
            refresh_token:
              type: string
              description: JWT refresh token
      400:
        description: Missing credentials
      401:
        description: Invalid credentials
      429:
        description: Too many login attempts
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Request body must be JSON'
            }), 400
        
        username_or_email = data.get('username_or_email', '').strip()
        password = data.get('password', '')
        
        if not username_or_email or not password:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Username/email and password are required'
            }), 400
        
        # Validate credentials
        admin, is_valid = validate_admin_credentials(username_or_email, password)
        
        if not is_valid or not admin:
            current_app.logger.warning(f'Failed login attempt for: {username_or_email}')
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Invalid username or password'
            }), 401
        
        # Create JWT tokens
        access_token = create_access_token(
            identity=str(admin.id),
            additional_claims={'role': 'admin'}
        )
        refresh_token = create_refresh_token(
            identity=str(admin.id),
            additional_claims={'role': 'admin'}
        )
        
        current_app.logger.info(f'Successful login for admin: {admin.username}')
        
        return jsonify({
            'message': 'Login successful',
            'admin': admin.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'Login error: {str(e)}')
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred during login'
        }), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh Access Token
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: Token refreshed successfully
        schema:
          type: object
          properties:
            access_token:
              type: string
              description: New JWT access token
      401:
        description: Invalid refresh token
    """
    try:
        admin_id = get_jwt_identity()
        
        # Verify admin still exists and is active
        admin = Admin.query.filter_by(id=int(admin_id), is_active=True).first()
        if not admin:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Admin account not found or inactive'
            }), 401
        
        # Create new access token
        access_token = create_access_token(
            identity=admin_id,
            additional_claims={'role': 'admin'}
        )
        
        return jsonify({
            'access_token': access_token
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'Token refresh error: {str(e)}')
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred during token refresh'
        }), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout Admin
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: Logout successful
        schema:
          type: object
          properties:
            message:
              type: string
              example: Logout successful
      401:
        description: Invalid token
    """
    try:
        token = get_jwt()
        jti = token['jti']  # JWT ID
        
        # Add token to revoked list (use Redis in production)
        revoked_tokens.add(jti)
        
        current_app.logger.info('Admin logged out successfully')
        
        return jsonify({
            'message': 'Logout successful'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'Logout error: {str(e)}')
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred during logout'
        }), 500


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Get Admin Profile
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: Profile retrieved successfully
        schema:
          type: object
          properties:
            admin:
              type: object
              properties:
                id:
                  type: integer
                username:
                  type: string
                email:
                  type: string
                is_active:
                  type: boolean
                created_at:
                  type: string
                updated_at:
                  type: string
      401:
        description: Invalid token
    """
    try:
        admin = get_current_admin()
        if not admin:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Admin not found'
            }), 401
        
        return jsonify({
            'admin': admin.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'Get profile error: {str(e)}')
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while fetching profile'
        }), 500


# JWT token verification callback setup (handled in app initialization)
