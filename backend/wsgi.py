"""
WSGI Entry Point for Employee Management System
"""
import os
from app import create_app

# Create Flask application
app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)