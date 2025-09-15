"""
Employee Model
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Numeric
from sqlalchemy.ext.hybrid import hybrid_property
from app.extensions import db


class Employee(db.Model):
    """Employee model with soft delete functionality."""
    
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    address = Column(String(200), nullable=True)
    department = Column(String(50), nullable=False, index=True)
    position = Column(String(50), nullable=False)
    salary = Column(Numeric(10, 2), nullable=False)  # Precision: 10 digits, 2 decimal places
    hire_date = Column(Date, nullable=False)
    status = Column(String(20), default='Active', nullable=False, index=True)  # 'Active' or 'Inactive'
    profile_picture_path = Column(String(200), nullable=True)
    
    # Soft delete fields
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Add composite indexes for better query performance
    __table_args__ = (
        db.Index('ix_employee_dept_status', 'department', 'status'),
        db.Index('ix_employee_active', 'is_deleted', 'status'),
    )
    
    @hybrid_property
    def is_active(self):
        """Check if employee is active and not deleted."""
        return not self.is_deleted and self.status == 'Active'
    
    def soft_delete(self):
        """Soft delete the employee."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        self.status = 'Inactive'
    
    def restore(self):
        """Restore a soft deleted employee."""
        self.is_deleted = False
        self.deleted_at = None
        self.status = 'Active'
    
    @classmethod
    def get_active_query(cls):
        """Get query for active (non-deleted) employees."""
        return cls.query.filter(cls.is_deleted == False)
    
    @classmethod
    def get_deleted_query(cls):
        """Get query for soft-deleted employees."""
        return cls.query.filter(cls.is_deleted == True)
    
    def to_dict(self, include_sensitive=False):
        """Convert employee to dictionary."""
        data = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'department': self.department,
            'position': self.position,
            'salary': float(self.salary) if self.salary is not None else None,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'status': self.status,
            'profile_picture_path': self.profile_picture_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_sensitive:
            data.update({
                'is_deleted': self.is_deleted,
                'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None
            })
        
        return data
    
    def __repr__(self):
        return f'<Employee {self.name} ({self.email})>'