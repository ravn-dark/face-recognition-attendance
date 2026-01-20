"""
Database models for Attendance System
"""

from datetime import datetime
from models.database import db

class Student(db.Model):
    """Student model"""
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    course = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with attendance records
    attendance_records = db.relationship('Attendance', backref='student', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Student {self.student_id}: {self.name}>'
    
    def to_dict(self):
        """Convert student to dictionary"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'name': self.name,
            'email': self.email,
            'course': self.course,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Attendance(db.Model):
    """Attendance record model"""
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='present')  # present, absent, late
    method = db.Column(db.String(20), default='face_recognition')  # face_recognition, manual
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint: one attendance record per student per day
    __table_args__ = (db.UniqueConstraint('student_id', 'date', name='unique_student_date'),)
    
    def __repr__(self):
        return f'<Attendance {self.student_id} on {self.date}: {self.status}>'
    
    def to_dict(self):
        """Convert attendance record to dictionary"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'date': self.date.isoformat() if self.date else None,
            'time': self.time.isoformat() if self.time else None,
            'status': self.status,
            'method': self.method,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
