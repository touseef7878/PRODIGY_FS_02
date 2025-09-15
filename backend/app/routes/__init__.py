"""
Routes Package
"""
from flask import Blueprint

# Import blueprints
from .auth import auth_bp
from .employees import employees_bp


__all__ = ['auth_bp', 'employees_bp']