"""
Database models package
"""

from models.database import db
from models.models import Student, Attendance

__all__ = ['db', 'Student', 'Attendance']
