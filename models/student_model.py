"""
SQLite database models for Attendance System
Using Python sqlite3 module
"""

import sqlite3
import os
import pickle
from datetime import datetime, date, time
from pathlib import Path

# Database path
BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / 'attendance.db'

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn

def create_tables():
    """Create students and attendance tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Create students table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                course TEXT,
                face_encoding BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create admin table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert default admin if not exists
        cursor.execute('SELECT COUNT(*) FROM admin')
        if cursor.fetchone()[0] == 0:
            import hashlib
            default_password = hashlib.sha256('admin123'.encode()).hexdigest()
            cursor.execute('''
                INSERT INTO admin (username, password)
                VALUES (?, ?)
            ''', ('admin', default_password))
        
        # Create index on student_id for faster lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_student_id 
            ON students(student_id)
        ''')
        
        # Create attendance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                date DATE NOT NULL,
                time TIME NOT NULL,
                status TEXT DEFAULT 'present',
                method TEXT DEFAULT 'face_recognition',
                confidence_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id),
                UNIQUE(student_id, date)
            )
        ''')
        
        # Create indexes for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_attendance_student_id 
            ON attendance(student_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_attendance_date 
            ON attendance(date)
        ''')
        
        conn.commit()
        print("Tables created successfully")
        
    except sqlite3.Error as e:
        print(f"Error creating tables: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def add_student(student_id, name, email, course=None, face_encoding=None):
    """
    Add a new student to the database
    
    Args:
        student_id (str): Unique student identifier
        name (str): Student's full name
        email (str): Student's email address
        course (str, optional): Course name
        face_encoding (bytes, optional): Pickled face encoding data
    
    Returns:
        int: ID of the newly created student, or None if error
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Pickle the face encoding if provided
        face_encoding_blob = None
        if face_encoding is not None:
            face_encoding_blob = pickle.dumps(face_encoding)
        
        cursor.execute('''
            INSERT INTO students (student_id, name, email, course, face_encoding)
            VALUES (?, ?, ?, ?, ?)
        ''', (student_id, name, email, course, face_encoding_blob))
        
        conn.commit()
        student_db_id = cursor.lastrowid
        print(f"Student added successfully with ID: {student_db_id}")
        return student_db_id
        
    except sqlite3.IntegrityError as e:
        print(f"Error adding student: {e}")
        conn.rollback()
        return None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

def get_all_students():
    """
    Get all students from the database
    
    Returns:
        list: List of dictionaries containing student information
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT id, student_id, name, email, course, face_encoding, created_at
            FROM students
            ORDER BY created_at DESC
        ''')
        
        rows = cursor.fetchall()
        students = []
        
        for row in rows:
            students.append({
                'id': row['id'],
                'student_id': row['student_id'],
                'name': row['name'],
                'email': row['email'],
                'course': row['course'],
                'face_encoding': row['face_encoding'],  # BLOB data
                'created_at': row['created_at']
            })
        
        return students
        
    except sqlite3.Error as e:
        print(f"Error fetching students: {e}")
        return []
    finally:
        conn.close()

def mark_attendance(student_id, date_str=None, time_str=None, status='present', method='face_recognition', confidence_score=None):
    """
    Mark attendance for a student
    
    Args:
        student_id (str): Student's unique identifier (student_id, not database id)
        date_str (str, optional): Date in 'YYYY-MM-DD' format. Defaults to today
        time_str (str, optional): Time in 'HH:MM:SS' format. Defaults to current time
        status (str): Attendance status ('present', 'absent', 'late'). Defaults to 'present'
        method (str): Method used ('face_recognition', 'manual'). Defaults to 'face_recognition'
        confidence_score (float, optional): Confidence score of face recognition match
    
    Returns:
        int: ID of the attendance record, or None if error
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get student's database ID from student_id
        cursor.execute('SELECT id FROM students WHERE student_id = ?', (student_id,))
        student_row = cursor.fetchone()
        
        if not student_row:
            print(f"Student with student_id '{student_id}' not found")
            return None
        
        student_db_id = student_row['id']
        
        # Use current date/time if not provided
        if date_str is None:
            attendance_date = date.today()
        else:
            attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        if time_str is None:
            attendance_time = datetime.now().time()
        else:
            attendance_time = datetime.strptime(time_str, '%H:%M:%S').time()
        
        # Insert attendance record
        cursor.execute('''
            INSERT INTO attendance (student_id, date, time, status, method, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (student_db_id, attendance_date, attendance_time, status, method, confidence_score))
        
        conn.commit()
        attendance_id = cursor.lastrowid
        print(f"Attendance marked successfully with ID: {attendance_id}")
        return attendance_id
        
    except sqlite3.IntegrityError as e:
        print(f"Error marking attendance: Attendance already exists for this student on this date")
        conn.rollback()
        return None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
        return None
    except ValueError as e:
        print(f"Date/time format error: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

def check_attendance_today(student_id):
    """
    Check if student has already marked attendance today
    
    Args:
        student_id (str): Student's unique identifier
    
    Returns:
        bool: True if attendance already marked today, False otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        today = date.today()
        cursor.execute('''
            SELECT COUNT(*) 
            FROM attendance a
            INNER JOIN students s ON a.student_id = s.id
            WHERE s.student_id = ? AND a.date = ?
        ''', (student_id, today))
        
        count = cursor.fetchone()[0]
        return count > 0
        
    except sqlite3.Error as e:
        print(f"Error checking attendance: {e}")
        return False
    finally:
        conn.close()

def get_attendance_by_date(date_str=None):
    """
    Get all attendance records for a specific date
    
    Args:
        date_str (str, optional): Date in 'YYYY-MM-DD' format. Defaults to today
    
    Returns:
        list: List of dictionaries containing attendance information
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Use today's date if not provided
        if date_str is None:
            attendance_date = date.today()
        else:
            attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        cursor.execute('''
            SELECT 
                a.id,
                a.student_id,
                s.student_id as student_identifier,
                s.name,
                s.email,
                s.course,
                a.date,
                a.time,
                a.status,
                a.method,
                a.confidence_score,
                a.created_at
            FROM attendance a
            INNER JOIN students s ON a.student_id = s.id
            WHERE a.date = ?
            ORDER BY a.time ASC
        ''', (attendance_date,))
        
        rows = cursor.fetchall()
        attendance_records = []
        
        for row in rows:
            attendance_records.append({
                'id': row['id'],
                'student_id': row['student_id'],  # Database ID
                'student_identifier': row['student_identifier'],  # Student's unique ID
                'name': row['name'],
                'email': row['email'],
                'course': row['course'],
                'date': row['date'],
                'time': row['time'],
                'status': row['status'],
                'method': row['method'],
                'confidence_score': row['confidence_score'],
                'created_at': row['created_at']
            })
        
        return attendance_records
        
    except sqlite3.Error as e:
        print(f"Error fetching attendance: {e}")
        return []
    except ValueError as e:
        print(f"Date format error: {e}")
        return []
    finally:
        conn.close()

def get_all_attendance_records(student_id_filter=None, date_filter=None, limit=None):
    """
    Get all attendance records with optional filters
    
    Args:
        student_id_filter (str, optional): Filter by student_id
        date_filter (str, optional): Filter by date in 'YYYY-MM-DD' format
        limit (int, optional): Limit number of records returned
    
    Returns:
        list: List of dictionaries containing attendance information
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = '''
            SELECT 
                a.id,
                a.student_id,
                s.student_id as student_identifier,
                s.name,
                s.email,
                s.course,
                a.date,
                a.time,
                a.status,
                a.method,
                a.confidence_score,
                a.created_at
            FROM attendance a
            INNER JOIN students s ON a.student_id = s.id
            WHERE 1=1
        '''
        params = []
        
        if student_id_filter:
            query += ' AND s.student_id = ?'
            params.append(student_id_filter)
        
        if date_filter:
            try:
                attendance_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                query += ' AND a.date = ?'
                params.append(attendance_date)
            except ValueError:
                pass  # Invalid date format, ignore filter
        
        query += ' ORDER BY a.date DESC, a.time DESC'
        
        if limit:
            query += ' LIMIT ?'
            params.append(limit)
        
        cursor.execute(query, params)
        
        rows = cursor.fetchall()
        attendance_records = []
        
        for row in rows:
            attendance_records.append({
                'id': row['id'],
                'student_id': row['student_id'],  # Database ID
                'student_identifier': row['student_identifier'],  # Student's unique ID
                'name': row['name'],
                'email': row['email'],
                'course': row['course'],
                'date': row['date'],
                'time': row['time'],
                'status': row['status'],
                'method': row['method'],
                'confidence_score': row['confidence_score'],
                'created_at': row['created_at']
            })
        
        return attendance_records
        
    except sqlite3.Error as e:
        print(f"Error fetching attendance records: {e}")
        return []
    finally:
        conn.close()

def get_student_face_encoding(student_id):
    """
    Get face encoding for a student by student_id
    
    Args:
        student_id (str): Student's unique identifier
    
    Returns:
        numpy.ndarray or None: Face encoding if found, None otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT face_encoding
            FROM students
            WHERE student_id = ?
        ''', (student_id,))
        
        row = cursor.fetchone()
        if row and row['face_encoding']:
            return pickle.loads(row['face_encoding'])
        return None
        
    except sqlite3.Error as e:
        print(f"Error fetching face encoding: {e}")
        return None
    except Exception as e:
        print(f"Error unpickling face encoding: {e}")
        return None
    finally:
        conn.close()

def get_all_face_encodings():
    """
    Get all student face encodings for recognition
    
    Returns:
        dict: Dictionary mapping student_id to (face_encoding, name)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT student_id, name, face_encoding
            FROM students
            WHERE face_encoding IS NOT NULL
        ''')
        
        rows = cursor.fetchall()
        encodings = {}
        
        for row in rows:
            if row['face_encoding']:
                try:
                    encoding = pickle.loads(row['face_encoding'])
                    encodings[row['student_id']] = (encoding, row['name'])
                except Exception as e:
                    print(f"Error unpickling encoding for {row['student_id']}: {e}")
                    continue
        
        return encodings
        
    except sqlite3.Error as e:
        print(f"Error fetching face encodings: {e}")
        return {}
    finally:
        conn.close()

def get_student_by_student_id(student_id):
    """
    Get a student by their student_id
    
    Args:
        student_id (str): Student's unique identifier
    
    Returns:
        dict: Student information or None if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT id, student_id, name, email, course, created_at
            FROM students
            WHERE student_id = ?
        ''', (student_id,))
        
        row = cursor.fetchone()
        if row:
            return {
                'id': row['id'],
                'student_id': row['student_id'],
                'name': row['name'],
                'email': row['email'],
                'course': row['course'],
                'created_at': row['created_at']
            }
        return None
        
    except sqlite3.Error as e:
        print(f"Error fetching student: {e}")
        return None
    finally:
        conn.close()

def update_student(student_id, name=None, email=None, course=None):
    """
    Update student information
    
    Args:
        student_id (str): Student's unique identifier
        name (str, optional): Updated name
        email (str, optional): Updated email
        course (str, optional): Updated course
    
    Returns:
        bool: True if successful, False otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Build update query dynamically
        updates = []
        params = []
        
        if name is not None:
            updates.append('name = ?')
            params.append(name)
        
        if email is not None:
            updates.append('email = ?')
            params.append(email)
        
        if course is not None:
            updates.append('course = ?')
            params.append(course)
        
        if not updates:
            return True  # Nothing to update
        
        params.append(student_id)
        
        query = f'''
            UPDATE students
            SET {', '.join(updates)}
            WHERE student_id = ?
        '''
        
        cursor.execute(query, params)
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"Student {student_id} updated successfully")
            return True
        return False
        
    except sqlite3.IntegrityError as e:
        print(f"Error updating student: {e}")
        conn.rollback()
        return False
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def update_face_encoding(student_id, face_encoding):
    """
    Update face encoding for a student
    
    Args:
        student_id (str): Student's unique identifier
        face_encoding: Face encoding to store
    
    Returns:
        bool: True if successful, False otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        face_encoding_blob = pickle.dumps(face_encoding) if face_encoding is not None else None
        
        cursor.execute('''
            UPDATE students
            SET face_encoding = ?
            WHERE student_id = ?
        ''', (face_encoding_blob, student_id))
        
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"Face encoding updated for student {student_id}")
            return True
        return False
        
    except sqlite3.Error as e:
        print(f"Database error updating face encoding: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def delete_student(student_id):
    """
    Delete a student from the database
    
    Args:
        student_id (str): Student's unique identifier
    
    Returns:
        bool: True if successful, False otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get student's database ID first
        cursor.execute('SELECT id FROM students WHERE student_id = ?', (student_id,))
        student_row = cursor.fetchone()
        
        if not student_row:
            print(f"Student {student_id} not found")
            return False
        
        student_db_id = student_row['id']
        
        # Delete attendance records first (due to foreign key)
        cursor.execute('DELETE FROM attendance WHERE student_id = ?', (student_db_id,))
        
        # Delete student
        cursor.execute('DELETE FROM students WHERE student_id = ?', (student_id,))
        
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"Student {student_id} deleted successfully")
            return True
        return False
        
    except sqlite3.Error as e:
        print(f"Database error deleting student: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def get_attendance_by_date_range(start_date=None, end_date=None, limit=30):
    """
    Get attendance statistics grouped by date
    
    Args:
        start_date (date, optional): Start date for range
        end_date (date, optional): End date for range
        limit (int): Maximum number of days to return (default 30)
    
    Returns:
        list: List of dictionaries with date and count
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if start_date and end_date:
            query = '''
                SELECT 
                    a.date,
                    COUNT(*) as count
                FROM attendance a
                WHERE a.date BETWEEN ? AND ?
                GROUP BY a.date
                ORDER BY a.date DESC
            '''
            params = (start_date, end_date)
        else:
            # Get last N days
            query = '''
                SELECT 
                    a.date,
                    COUNT(*) as count
                FROM attendance a
                GROUP BY a.date
                ORDER BY a.date DESC
                LIMIT ?
            '''
            params = (limit,)
        
        cursor.execute(query, params)
        
        rows = cursor.fetchall()
        attendance_by_date = []
        
        for row in rows:
            attendance_by_date.append({
                'date': row['date'],
                'count': row['count']
            })
        
        return attendance_by_date
        
    except sqlite3.Error as e:
        print(f"Error fetching attendance by date: {e}")
        return []
    finally:
        conn.close()
