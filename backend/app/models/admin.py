"""
Admin Model
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.hybrid import hybrid_property
import bcrypt
from app.extensions import db


class Admin(db.Model):
    """Admin model for authentication and authorization."""
    
    __tablename__ = 'admins'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    _password_hash = Column('password_hash', String(128), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    @hybrid_property
    def password(self):
        """Prevent password from being accessed."""
        raise AttributeError('Password is not a readable attribute.')
    
    @password.setter
    def password(self, password):
        """Hash password when setting."""
        if password:
            self._password_hash = bcrypt.hashpw(
                password.encode('utf-8'), 
                bcrypt.gensalt()
            ).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches hash."""
        if not password or not self._password_hash:
            return False
        return bcrypt.checkpw(
            password.encode('utf-8'), 
            self._password_hash.encode('utf-8')
        )
    
    def to_dict(self):
        """Convert admin to dictionary (excluding sensitive data)."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Admin {self.username}>'