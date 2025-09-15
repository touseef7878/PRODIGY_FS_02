#!/usr/bin/env python3
"""
Create Initial Admin User
"""
import os
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import create_app
from app.extensions import db
from app.models import Admin


def create_initial_admin():
    """Create an initial admin user."""
    app = create_app('development')
    
    with app.app_context():
        # Check if any admin exists
        existing_admin = Admin.query.first()
        if existing_admin:
            print(f"Admin user already exists: {existing_admin.username}")
            return
        
        # Create default admin
        admin = Admin(
            username='admin',
            email='admin@prodigyinfotec.com',
            is_active=True
        )
        admin.password = 'ProdigyAdmin2024!'  # This will be hashed
        
        db.session.add(admin)
        db.session.commit()
        
        print("✅ Initial admin user created successfully!")
        print("👤 Username: admin")
        print("📧 Email: admin@prodigyinfotec.com")
        print("🔐 Password: ProdigyAdmin2024!")
        print("\n⚠️  Please change the password after first login!")


if __name__ == '__main__':
    create_initial_admin()