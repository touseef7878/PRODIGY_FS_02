"""
Validation Utilities
"""
import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import bleach


def validate_email(email):
    """Validate email format."""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone):
    """Validate phone number format."""
    if not phone:
        return True  # Phone is optional
    # Allow various phone formats: +1234567890, 123-456-7890, (123) 456-7890, etc.
    pattern = r'^[\+]?[1-9][\d\-\(\)\s]{7,15}$'
    return re.match(pattern, phone) is not None


def validate_salary(salary):
    """Validate salary amount."""
    if salary is None or salary == '':
        return False, "Salary is required"
    
    try:
        # Handle different input types
        if isinstance(salary, (int, float)):
            salary_decimal = Decimal(str(salary))
        elif isinstance(salary, str):
            # Remove any currency symbols or commas
            salary = salary.replace('$', '').replace(',', '').strip()
            if not salary:
                return False, "Salary is required"
            salary_decimal = Decimal(salary)
        else:
            salary_decimal = Decimal(str(salary))
            
        if salary_decimal <= 0:
            return False, "Salary must be greater than 0"
        if salary_decimal > Decimal('9999999.99'):
            return False, "Salary is too large"
        return True, float(salary_decimal)  # Return as float for consistency with model
    except (InvalidOperation, ValueError, TypeError):
        return False, "Invalid salary format"


def validate_hire_date(hire_date_str):
    """Validate hire date."""
    if not hire_date_str:
        return False, "Hire date is required"

    hire_date = None
    if isinstance(hire_date_str, date):
        hire_date = hire_date_str
    elif isinstance(hire_date_str, str):
        # Try different date formats
        formats_to_try = ('%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y')
        for fmt in formats_to_try:
            try:
                hire_date = datetime.strptime(hire_date_str, fmt).date()
                break
            except ValueError:
                continue
        else:
            return False, f"Invalid date format. Use one of: {', '.join(formats_to_try)}"
    else:
        # Try to convert to string and parse
        try:
            hire_date_str = str(hire_date_str)
            for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y'):
                try:
                    hire_date = datetime.strptime(hire_date_str, fmt).date()
                    break
                except ValueError:
                    continue
            else:
                return False, "Invalid date format"
        except:
            return False, "Invalid date format"

    # Check if hire date is not in the future
    if hire_date > date.today():
        return False, "Hire date cannot be in the future"

    # Check if hire date is not too far in the past (e.g., 100 years)
    if hire_date < date(date.today().year - 100, 1, 1):
        return False, "Hire date is too far in the past"

    return True, hire_date


def sanitize_text(text):
    """Sanitize text input to prevent XSS."""
    if not text:
        return text
    
    # Allow basic HTML tags if needed, or strip all
    allowed_tags = []  # No HTML tags allowed
    cleaned = bleach.clean(text, tags=allowed_tags, strip=True)
    return cleaned.strip()


def validate_department(department):
    """Validate department name."""
    if not department:
        return False, "Department is required"
    
    department = sanitize_text(department)
    if len(department) < 2:
        return False, "Department name must be at least 2 characters"
    if len(department) > 50:
        return False, "Department name must be less than 50 characters"
    
    return True, department


def validate_position(position):
    """Validate position/job title."""
    if not position:
        return False, "Position is required"
    
    position = sanitize_text(position)
    if len(position) < 2:
        return False, "Position must be at least 2 characters"
    if len(position) > 50:
        return False, "Position must be less than 50 characters"
    
    return True, position


def validate_name(name):
    """Validate employee name."""
    if not name:
        return False, "Name is required"
    
    name = sanitize_text(name)
    if len(name) < 2:
        return False, "Name must be at least 2 characters"
    if len(name) > 100:
        return False, "Name must be less than 100 characters"
    
    # Check for valid name characters (letters, spaces, hyphens, apostrophes)
    pattern = r"^[a-zA-Z\s\-'\.]+$"
    if not re.match(pattern, name):
        return False, "Name contains invalid characters"
    
    return True, name


def validate_status(status):
    """Validate employee status."""
    valid_statuses = ['Active', 'Inactive']
    if status not in valid_statuses:
        return False, f"Status must be one of: {', '.join(valid_statuses)}"
    return True, status


def validate_address(address):
    """Validate address."""
    if not address:
        return True, address  # Address is optional
    
    address = sanitize_text(address)
    if len(address) > 200:
        return False, "Address must be less than 200 characters"
    
    return True, address