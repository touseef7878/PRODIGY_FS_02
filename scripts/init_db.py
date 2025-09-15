#!/usr/bin/env python3
"""
Database Initialization Script
"""
import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
project_root = Path(__file__).parent.parent
backend_path = project_root / 'backend'
sys.path.insert(0, str(backend_path))

from app import create_app
from app.extensions import db
from app.models import Admin, Employee
from datetime import date


def init_database():
    """Initialize the database with tables and initial data."""
    print("[*] Initializing Employee Management System Database...")
    
    app = create_app('development')
    
    with app.app_context():
        try:
            # Drop all tables (uncomment if you want to reset everything)
            # print("⚠️  Dropping all existing tables...")
            # db.drop_all()
            
            # Create all tables
            print("[*] Creating database tables...")
            db.create_all()
            
            # Check if admin exists
            existing_admin = Admin.query.first()
            if existing_admin:
                print(f"[*] Admin user already exists: {existing_admin.username}")
            else:
                # Create initial admin
                print("[*] Creating initial admin user...")
                admin = Admin(
                    username=os.getenv('ADMIN_USERNAME', 'admin'),
                    email=os.getenv('ADMIN_EMAIL', 'admin@prodigyinfotec.com'),
                    is_active=True
                )
                admin.password = os.getenv('ADMIN_PASSWORD', 'ProdigyAdmin2024!')
                
                db.session.add(admin)
                print("[+] Initial admin user created!")
            
            # Check if sample employees exist
            existing_employees = Employee.query.count()
            if existing_employees == 0:
                print("[*] Creating sample employees...")
                sample_employees = [
                    {
                        'name': 'John Doe',
                        'email': 'john.doe@prodigyinfotec.com',
                        'phone': '+1-555-0101',
                        'address': '123 Main St, Tech City, TC 12345',
                        'department': 'Engineering',
                        'position': 'Senior Software Developer',
                        'salary': 85000.00,
                        'hire_date': date(2023, 1, 15),
                        'status': 'Active'
                    },
                    {
                        'name': 'Jane Smith',
                        'email': 'jane.smith@prodigyinfotec.com',
                        'phone': '+1-555-0102',
                        'address': '456 Oak Ave, Business Park, BP 67890',
                        'department': 'Human Resources',
                        'position': 'HR Manager',
                        'salary': 75000.00,
                        'hire_date': date(2023, 2, 1),
                        'status': 'Active'
                    },
                    {
                        'name': 'Mike Johnson',
                        'email': 'mike.johnson@prodigyinfotec.com',
                        'phone': '+1-555-0103',
                        'address': '789 Pine St, Innovation District, ID 11111',
                        'department': 'Marketing',
                        'position': 'Marketing Specialist',
                        'salary': 60000.00,
                        'hire_date': date(2023, 3, 10),
                        'status': 'Active'
                    },
                    {
                        'name': 'Sarah Wilson',
                        'email': 'sarah.wilson@prodigyinfotec.com',
                        'phone': '+1-555-0104',
                        'address': '321 Elm St, Corporate Center, CC 22222',
                        'department': 'Finance',
                        'position': 'Financial Analyst',
                        'salary': 70000.00,
                        'hire_date': date(2023, 4, 5),
                        'status': 'Active'
                    },
                    {
                        'name': 'David Brown',
                        'email': 'david.brown@prodigyinfotec.com',
                        'phone': '+1-555-0105',
                        'address': '654 Maple Ave, Tech Hub, TH 33333',
                        'department': 'Engineering',
                        'position': 'DevOps Engineer',
                        'salary': 80000.00,
                        'hire_date': date(2023, 5, 20),
                        'status': 'Active'
                    },
                    {
                        'name': 'Emily Davis',
                        'email': 'emily.davis@prodigyinfotec.com',
                        'phone': '+1-555-0106',
                        'address': '987 Cedar Ln, Business Square, BS 44444',
                        'department': 'Design',
                        'position': 'UX/UI Designer',
                        'salary': 65000.00,
                        'hire_date': date(2023, 6, 1),
                        'status': 'Active'
                    }
                ]
                
                for emp_data in sample_employees:
                    employee = Employee(**emp_data)
                    db.session.add(employee)
                
                print(f"[+] Created {len(sample_employees)} sample employees!")
            else:
                print(f"[*] {existing_employees} employees already exist in database")
            
            # Commit all changes
            db.session.commit()
            
            print("\\n[+] Database initialization completed successfully!")
            print("\\n[*] Database Summary:")
            print(f"   - Admins: {Admin.query.count()}")
            print(f"   - Employees: {Employee.query.count()}")
            print(f"   - Active Employees: {Employee.query.filter_by(status='Active', is_deleted=False).count()}")
            
            print("\\n[*] Admin Credentials:")
            admin = Admin.query.first()
            if admin:
                print(f"   - Username: {admin.username}")
                print(f"   - Email: {admin.email}")
                print(f"   - Password: {os.getenv('ADMIN_PASSWORD', 'ProdigyAdmin2024!')}")
            
            print("\\n[+] You can now start the application!")
            print("   - Run: python backend/wsgi.py")
            print("   - API Docs: http://localhost:5000/api/docs/")
            
        except Exception as e:
            print(f"[!] Error initializing database: {str(e)}")
            db.session.rollback()
            sys.exit(1)


def reset_database():
    """Reset the database (drop all tables and recreate)."""
    print("[!] WARNING: This will delete ALL data in the database!")
    confirm = input("Are you sure you want to reset the database? (yes/NO): ")
    
    if confirm.lower() != 'yes':
        print("[!] Database reset cancelled.")
        return
    
    print("[*] Resetting database...")
    
    app = create_app('development')
    
    with app.app_context():
        try:
            # Drop all tables
            db.drop_all()
            print("[+] All tables dropped.")
            
            # Recreate tables
            db.create_all()
            print("[+] Tables recreated.")
            
            print("[+] Database reset completed. Run init_db.py to populate with initial data.")
            
        except Exception as e:
            print(f"[!] Error resetting database: {str(e)}")
            sys.exit(1)


if __name__ == '__main__':
    # Check if reset flag is provided
    if len(sys.argv) > 1 and sys.argv[1] == '--reset':
        reset_database()
    else:
        init_database()