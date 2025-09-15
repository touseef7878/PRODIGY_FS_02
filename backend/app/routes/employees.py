"""
Employee Routes
"""
import os
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from flask import Blueprint, request, jsonify, current_app, send_from_directory, Response
from flask_jwt_extended import jwt_required
from sqlalchemy import or_, and_
from werkzeug.utils import secure_filename
from flasgger import swag_from

from app.extensions import db, limiter
from app.models.employee import Employee
from app.utils.security import admin_required
from app.utils.validators import (
    validate_email, validate_phone, validate_salary, validate_hire_date,
    validate_department, validate_position, validate_name, validate_status,
    validate_address
)

employees_bp = Blueprint('employees', __name__)

# Allowed file extensions for profile pictures
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@employees_bp.route('', methods=['GET'])
@admin_required
def get_employees(admin):
    """
    Get All Employees with Pagination and Search
    ---
    tags:
      - Employees
    security:
      - Bearer: []
    parameters:
      - in: query
        name: page
        type: integer
        description: 'Page number (default: 1)'
        default: 1
      - in: query
        name: per_page
        type: integer
        description: 'Items per page (default: 10, max: 100)'
        default: 10
      - in: query
        name: search
        type: string
        description: 'Search term for name, email, department, or position'
      - in: query
        name: department
        type: string
        description: 'Filter by department'
      - in: query
        name: status
        type: string
        description: 'Filter by status (Active/Inactive)'
      - in: query
        name: include_deleted
        type: boolean
        description: 'Include soft-deleted employees (default: false)'
        default: false
    responses:
      200:
        description: Employees retrieved successfully
        schema:
          type: object
          properties:
            employees:
              type: array
              items:
                type: object
            pagination:
              type: object
              properties:
                page:
                  type: integer
                per_page:
                  type: integer
                total:
                  type: integer
                pages:
                  type: integer
                has_prev:
                  type: boolean
                has_next:
                  type: boolean
      401:
        description: Unauthorized
    """
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        search = request.args.get('search', '').strip()
        department_filter = request.args.get('department', '').strip()
        status_filter = request.args.get('status', '').strip()
        include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
        
        # Base query
        if include_deleted:
            query = Employee.query
        else:
            query = Employee.get_active_query()
        
        # Apply search filter
        if search:
            search_filter = or_(
                Employee.name.ilike(f'%{search}%'),
                Employee.email.ilike(f'%{search}%'),
                Employee.department.ilike(f'%{search}%'),
                Employee.position.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)
        
        # Apply department filter
        if department_filter:
            query = query.filter(Employee.department.ilike(f'%{department_filter}%'))
        
        # Apply status filter
        if status_filter:
            query = query.filter(Employee.status == status_filter)
        
        # Order by name
        query = query.order_by(Employee.name)
        
        # Paginate
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        employees = [
            employee.to_dict(include_sensitive=include_deleted)
            for employee in pagination.items
        ]
        
        return jsonify({
            'employees': employees,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_prev': pagination.has_prev,
                'has_next': pagination.has_next
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'Get employees error: {str(e)}')
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while fetching employees'
        }), 500


@employees_bp.route('/<int:employee_id>', methods=['GET'])
@admin_required
def get_employee(admin, employee_id):
    """
    Get Employee by ID
    ---
    tags:
      - Employees
    security:
      - Bearer: []
    parameters:
      - in: path
        name: employee_id
        type: integer
        required: true
        description: 'Employee ID'
      - in: query
        name: include_deleted
        type: boolean
        description: 'Include soft-deleted employee (default: false)'
        default: false
    responses:
      200:
        description: Employee retrieved successfully
        schema:
          type: object
          properties:
            employee:
              type: object
      404:
        description: Employee not found
      401:
        description: Unauthorized
    """
    try:
        include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
        
        if include_deleted:
            employee = Employee.query.get(employee_id)
        else:
            employee = Employee.get_active_query().filter_by(id=employee_id).first()
        
        if not employee:
            return jsonify({
                'error': 'Not Found',
                'message': 'Employee not found'
            }), 404
        
        return jsonify({
            'employee': employee.to_dict(include_sensitive=include_deleted)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'Get employee error: {str(e)}')
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while fetching employee'
        }), 500


@employees_bp.route('', methods=['POST'])
@admin_required
def create_employee(admin):
    """
    Create New Employee (Simplified)
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Request body must be JSON'
            }), 400
        
        # Extract data
        name = data.get('name')
        email = data.get('email')
        department = data.get('department')
        position = data.get('position')
        salary = data.get('salary')
        hire_date_str = data.get('hire_date')
        
        # Convert hire_date string to date object
        hire_date = datetime.strptime(hire_date_str, '%Y-%m-%d').date() if hire_date_str else None

        # Create employee
        employee = Employee(
            name=name,
            email=email,
            department=department,
            position=position,
            salary=salary,
            hire_date=hire_date,
        )
        
        db.session.add(employee)
        db.session.commit()
        
        return jsonify({
            'message': 'Employee created successfully (simplified)',
            'employee': employee.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        # Log the error so we can see what's happening
        current_app.logger.error(f'Create employee error: {str(e)}')
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


@employees_bp.route('/<int:employee_id>', methods=['PUT'])
@admin_required
def update_employee(admin, employee_id):
    """
    Update Employee
    ---
    tags:
      - Employees
    security:
      - Bearer: []
    parameters:
      - in: path
        name: employee_id
        type: integer
        required: true
        description: Employee ID
      - in: body
        name: employee
        description: Employee data to update
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            email:
              type: string
            phone:
              type: string
            address:
              type: string
            department:
              type: string
            position:
              type: string
            salary:
              type: number
            hire_date:
              type: string
              format: date
            status:
              type: string
              enum: [Active, Inactive]
    responses:
      200:
        description: Employee updated successfully
      400:
        description: Validation error
      404:
        description: Employee not found
      409:
        description: Email already exists
      401:
        description: Unauthorized
    """
    try:
        employee = Employee.get_active_query().filter_by(id=employee_id).first()
        
        if not employee:
            return jsonify({
                'error': 'Not Found',
                'message': 'Employee not found'
            }), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Request body must be JSON'
            }), 400
        
        errors = []
        
        # Update fields if provided
        if 'name' in data:
            name = data['name'].strip()
            is_valid, result = validate_name(name)
            if not is_valid:
                errors.append(f"Name: {result}")
            else:
                employee.name = result
        
        if 'email' in data:
            email = data['email'].strip().lower()
            if not validate_email(email):
                errors.append("Email: Invalid email format")
            else:
                # Check for duplicate email (excluding current employee)
                existing_employee = Employee.query.filter(
                    Employee.email == email,
                    Employee.id != employee_id
                ).first()
                if existing_employee:
                    errors.append("Email: Employee with this email already exists")
                else:
                    employee.email = email
        
        if 'phone' in data:
            phone = data['phone'].strip()
            if phone and not validate_phone(phone):
                errors.append("Phone: Invalid phone format")
            else:
                employee.phone = phone or None
        
        if 'department' in data:
            department = data['department'].strip()
            is_valid, result = validate_department(department)
            if not is_valid:
                errors.append(f"Department: {result}")
            else:
                employee.department = result
        
        if 'position' in data:
            position = data['position'].strip()
            is_valid, result = validate_position(position)
            if not is_valid:
                errors.append(f"Position: {result}")
            else:
                employee.position = result
        
        if 'salary' in data:
            salary = data['salary']
            is_valid, result = validate_salary(salary)
            if not is_valid:
                errors.append(f"Salary: {result}")
            else:
                employee.salary = result
        
        if 'hire_date' in data:
            hire_date_str = data['hire_date'].strip()
            is_valid, result = validate_hire_date(hire_date_str)
            if not is_valid:
                errors.append(f"Hire date: {result}")
            else:
                employee.hire_date = result
        
        if 'status' in data:
            status = data['status'].strip()
            is_valid, result = validate_status(status)
            if not is_valid:
                errors.append(f"Status: {result}")
            else:
                employee.status = result
        
        if 'address' in data:
            address = data['address'].strip()
            is_valid, result = validate_address(address)
            if not is_valid:
                errors.append(f"Address: {result}")
            else:
                employee.address = result
        
        if errors:
            return jsonify({
                'error': 'Validation Error',
                'message': 'Please correct the following errors',
                'errors': errors
            }), 400
        
        db.session.commit()
        
        current_app.logger.info(f'Employee updated: {employee.name} by admin {admin.username}')
        
        return jsonify({
            'message': 'Employee updated successfully',
            'employee': employee.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Update employee error: {str(e)}')
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while updating employee'
        }), 500


@employees_bp.route('/<int:employee_id>', methods=['DELETE'])
@admin_required
def delete_employee(admin, employee_id):
    """
    Delete Employee (Soft Delete)
    ---
    tags:
      - Employees
    security:
      - Bearer: []
    parameters:
      - in: path
        name: employee_id
        type: integer
        required: true
        description: 'Employee ID'
      - in: query
        name: permanent
        type: boolean
        description: 'Permanently delete employee (default: false)'
        default: false
    responses:
      200:
        description: Employee deleted successfully
      404:
        description: Employee not found
      401:
        description: Unauthorized
    """
    try:
        permanent = request.args.get('permanent', 'false').lower() == 'true'
        
        employee = Employee.get_active_query().filter_by(id=employee_id).first()
        
        if not employee:
            return jsonify({
                'error': 'Not Found',
                'message': 'Employee not found'
            }), 404
        
        if permanent:
            # Permanent delete (use with caution)
            db.session.delete(employee)
            message = 'Employee permanently deleted'
        else:
            # Soft delete
            employee.soft_delete()
            message = 'Employee deleted successfully'
        
        db.session.commit()
        
        current_app.logger.info(f'Employee deleted: {employee.name} by admin {admin.username} (permanent={permanent})')
        
        return jsonify({
            'message': message
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Delete employee error: {str(e)}')
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while deleting employee'
        }), 500


@employees_bp.route('/<int:employee_id>/restore', methods=['POST'])
@admin_required
def restore_employee(admin, employee_id):
    """
    Restore Soft-Deleted Employee
    ---
    tags:
      - Employees
    security:
      - Bearer: []
    parameters:
      - in: path
        name: employee_id
        type: integer
        required: true
        description: Employee ID
    responses:
      200:
        description: Employee restored successfully
      404:
        description: Employee not found
      400:
        description: Employee is not deleted or email conflict
      401:
        description: Unauthorized
    """
    try:
        employee = Employee.query.filter_by(id=employee_id, is_deleted=True).first()
        
        if not employee:
            return jsonify({
                'error': 'Not Found',
                'message': 'Deleted employee not found'
            }), 404
        
        # Check for email conflict
        existing_employee = Employee.query.filter(
            Employee.email == employee.email,
            Employee.id != employee_id,
            Employee.is_deleted == False
        ).first()
        
        if existing_employee:
            return jsonify({
                'error': 'Conflict',
                'message': 'Cannot restore: Another active employee with this email exists'
            }), 400
        
        employee.restore()
        db.session.commit()
        
        current_app.logger.info(f'Employee restored: {employee.name} by admin {admin.username}')
        
        return jsonify({
            'message': 'Employee restored successfully',
            'employee': employee.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Restore employee error: {str(e)}')
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while restoring employee'
        }), 500


@employees_bp.route('/<int:employee_id>/upload-profile', methods=['POST'])
@admin_required
@limiter.limit("5 per minute")
def upload_profile_picture(admin, employee_id):
    """
    Upload Employee Profile Picture
    ---
    tags:
      - Employees
    security:
      - Bearer: []
    consumes:
      - multipart/form-data
    parameters:
      - in: path
        name: employee_id
        type: integer
        required: true
        description: Employee ID
      - in: formData
        name: file
        type: file
        required: true
        description: 'Profile picture file (PNG, JPG, JPEG, GIF, WEBP)'
    responses:
      200:
        description: Profile picture uploaded successfully
      400:
        description: Invalid file or no file provided
      404:
        description: Employee not found
      413:
        description: File too large
      401:
        description: Unauthorized
    """
    try:
        employee = Employee.get_active_query().filter_by(id=employee_id).first()
        
        if not employee:
            return jsonify({
                'error': 'Not Found',
                'message': 'Employee not found'
            }), 404
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'error': 'Bad Request',
                'message': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'error': 'Bad Request',
                'message': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'error': 'Bad Request',
                'message': f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Create upload directory
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profiles')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate secure filename
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name_part, ext_part = os.path.splitext(filename)
        new_filename = f'employee_{employee_id}_{timestamp}{ext_part}'
        file_path = os.path.join(upload_dir, new_filename)
        
        # Delete old profile picture if exists
        if employee.profile_picture_path:
            old_file_path = os.path.join(
                current_app.config['UPLOAD_FOLDER'],
                employee.profile_picture_path
            )
            if os.path.exists(old_file_path):
                try:
                    os.remove(old_file_path)
                except OSError:
                    pass  # File might be in use or already deleted
        
        # Save file
        file.save(file_path)
        
        # Verify file was saved
        normalized_file_path = file_path.replace('/', os.sep)
        if not os.path.exists(normalized_file_path):
            current_app.logger.error(f"File was not saved correctly: {normalized_file_path}")
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'File was not saved correctly'
            }), 500
        
        # Update employee record with normalized path
        employee.profile_picture_path = os.path.join('profiles', new_filename).replace('\\', '/')
        db.session.commit()
        
        # Log the full path for debugging
        full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], employee.profile_picture_path.replace('/', os.sep))
        current_app.logger.info(f'Profile picture uploaded for employee: {employee.name} by admin {admin.username}')
        current_app.logger.info(f'Profile picture path saved: {employee.profile_picture_path}')
        current_app.logger.info(f'Full file path: {full_path}')
        current_app.logger.info(f'File exists: {os.path.exists(full_path)}')
        
        return jsonify({
            'message': 'Profile picture uploaded successfully',
            'profile_picture_path': employee.profile_picture_path
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Upload profile picture error: {str(e)}')
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while uploading profile picture'
        }), 500


@employees_bp.route('/<int:employee_id>/profile-picture', methods=['GET'])
def get_profile_picture(employee_id):
    """
    Get Employee Profile Picture
    ---
    tags:
      - Employees
    parameters:
      - in: path
        name: employee_id
        type: integer
        required: true
        description: Employee ID
    responses:
      200:
        description: Profile picture file
      404:
        description: Employee or picture not found
    """
    try:
        # Log the request
        current_app.logger.info(f"Profile picture request for employee ID: {employee_id}")
        
        # First try to get active employee, if not found try deleted employee
        employee = Employee.get_active_query().filter_by(id=employee_id).first()
        is_deleted = False
        
        if not employee:
            # Check if it's a deleted employee
            employee = Employee.query.filter_by(id=employee_id, is_deleted=True).first()
            is_deleted = True
            if employee:
                current_app.logger.info(f"Employee {employee_id} is deleted but profile picture requested")
            else:
                current_app.logger.info(f"Employee not found: {employee_id}")
                return jsonify({
                    'error': 'Not Found',
                    'message': 'Employee not found'
                }), 404
        else:
            current_app.logger.info(f"Employee found: {employee.name}")
            
        if not employee.profile_picture_path:
            current_app.logger.info(f"No profile picture path for employee: {employee_id}")
            return jsonify({
                'error': 'Not Found',
                'message': 'Profile picture not found'
            }), 404
        
        # Construct the full path to the profile picture
        upload_folder = current_app.config['UPLOAD_FOLDER']
        picture_path = employee.profile_picture_path
        
        # Normalize the path separators
        normalized_picture_path = picture_path.replace('/', os.sep).replace('\\', os.sep)
        full_path = os.path.join(upload_folder, normalized_picture_path)
        
        # Log all paths for debugging
        current_app.logger.info(f"Upload folder: {upload_folder}")
        current_app.logger.info(f"Picture path from DB: {picture_path}")
        current_app.logger.info(f"Normalized path: {normalized_picture_path}")
        current_app.logger.info(f"Full constructed path: {full_path}")
        current_app.logger.info(f"File exists: {os.path.exists(full_path)}")
        
        # Check if file exists
        if not os.path.exists(full_path):
            current_app.logger.error(f"Profile picture file not found: {full_path}")
            return jsonify({
                'error': 'Not Found',
                'message': 'Profile picture file not found on server'
            }), 404
        
        # Try to send the file directly
        try:
            return send_from_directory(upload_folder, normalized_picture_path)
        except Exception as send_error:
            current_app.logger.error(f"Error using send_from_directory: {str(send_error)}")
            # Fallback: read and return file directly
            try:
                with open(full_path, 'rb') as f:
                    content = f.read()
                
                # Determine content type based on file extension
                ext = os.path.splitext(full_path)[1].lower()
                content_type = 'image/jpeg'  # default
                if ext == '.png':
                    content_type = 'image/png'
                elif ext in ['.gif']:
                    content_type = 'image/gif'
                elif ext in ['.webp']:
                    content_type = 'image/webp'
                
                return Response(content, mimetype=content_type)
            except Exception as read_error:
                current_app.logger.error(f"Error reading file directly: {str(read_error)}")
                raise read_error
        
    except Exception as e:
        current_app.logger.error(f'Get profile picture error: {str(e)}', exc_info=True)
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while fetching profile picture'
        }), 500


@employees_bp.route('/stats', methods=['GET'])
@admin_required
def get_employee_stats(admin):
    """
    Get Employee Statistics
    ---
    tags:
      - Employees
    security:
      - Bearer: []
    responses:
      200:
        description: Employee statistics
        schema:
          type: object
          properties:
            total_employees:
              type: integer
            active_employees:
              type: integer
            inactive_employees:
              type: integer
            deleted_employees:
              type: integer
            departments:
              type: array
              items:
                type: object
                properties:
                  department:
                    type: string
                  count:
                    type: integer
      401:
        description: Unauthorized
    """
    try:
        # Basic counts
        total_employees = Employee.query.count()
        active_employees = Employee.query.filter_by(status='Active', is_deleted=False).count()
        inactive_employees = Employee.query.filter_by(status='Inactive', is_deleted=False).count()
        deleted_employees = Employee.query.filter_by(is_deleted=True).count()
        
        # Department statistics
        dept_stats = db.session.query(
            Employee.department,
            db.func.count(Employee.id).label('count')
        ).filter(Employee.is_deleted == False).group_by(Employee.department).all()
        
        departments = [
            {'department': dept, 'count': count}
            for dept, count in dept_stats
        ]
        
        return jsonify({
            'total_employees': total_employees,
            'active_employees': active_employees,
            'inactive_employees': inactive_employees,
            'deleted_employees': deleted_employees,
            'departments': departments
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'Get employee stats error: {str(e)}')
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while fetching statistics'
        }), 500