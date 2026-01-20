"""
Automated Attendance System Using Computer Vision
Main Flask Application
"""

import os
import cv2
import pickle
import csv
import io
import threading
import numpy as np
from datetime import date, datetime
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, flash, redirect, url_for, Response, make_response, session
from functools import wraps
import hashlib
import re
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("WARNING: face_recognition library not available. Face recognition features will be disabled.")
    print("Install dlib and face-recognition to enable face recognition:")
    print("  1. Install CMake from https://cmake.org/download/")
    print("  2. Run: python -m pip install dlib")
    print("  3. Run: python -m pip install face-recognition")

from models.student_model import create_tables, add_student, get_all_face_encodings, mark_attendance, check_attendance_today, get_all_attendance_records, get_all_students, get_student_by_student_id, update_student, delete_student, update_face_encoding, get_attendance_by_date, get_attendance_by_date_range
from config import Config

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Create database tables on startup
    create_tables()
    
    # Ensure faces directory exists
    faces_dir = Path(app.config['FACES_FOLDER'])
    os.makedirs(faces_dir, exist_ok=True)
    
    def allowed_file(filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
    
    # Login required decorator
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'admin_logged_in' not in session:
                flash('Please login to access this page', 'warning')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    
    # Validation functions
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_student_id(student_id):
        """Validate student ID format"""
        if not student_id or len(student_id.strip()) == 0:
            return False
        if len(student_id) > 50:
            return False
        return True
    
    def validate_name(name):
        """Validate name format"""
        if not name or len(name.strip()) < 2:
            return False
        if len(name) > 100:
            return False
        return True
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Admin login"""
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            
            if not username or not password:
                flash('Username and password are required', 'error')
                return render_template('login.html')
            
            # Check credentials
            if username == config_class.ADMIN_USERNAME and password == config_class.ADMIN_PASSWORD:
                session['admin_logged_in'] = True
                session['admin_username'] = username
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'error')
                return render_template('login.html')
        
        # If already logged in, redirect to dashboard
        if 'admin_logged_in' in session:
            return redirect(url_for('dashboard'))
        
        return render_template('login.html')
    
    @app.route('/logout')
    def logout():
        """Admin logout"""
        session.clear()
        flash('Logged out successfully', 'success')
        return redirect(url_for('login'))
    
    @app.route('/')
    def index():
        """Home page"""
        return render_template('index.html')
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Dashboard page with statistics and charts"""
        from datetime import timedelta
        
        # Get statistics
        all_students = get_all_students()
        total_students = len(all_students)
        
        # Get today's attendance
        today = date.today()
        today_attendance = get_attendance_by_date(today.isoformat())
        today_count = len(today_attendance)
        
        # Calculate attendance rate
        attendance_rate = (today_count / total_students * 100) if total_students > 0 else 0
        
        # Get date-wise attendance (last 30 days)
        end_date = today
        start_date = today - timedelta(days=29)
        date_wise_attendance = get_attendance_by_date_range(start_date, end_date, limit=30)
        
        # Get recent attendance records (last 10)
        recent_records = get_all_attendance_records(limit=10)
        
        # Prepare chart data
        chart_labels = [item['date'] for item in reversed(date_wise_attendance)]
        chart_data = [item['count'] for item in reversed(date_wise_attendance)]
        
        return render_template('dashboard.html',
                             total_students=total_students,
                             today_count=today_count,
                             attendance_rate=round(attendance_rate, 1),
                             recent_records=recent_records,
                             chart_labels=chart_labels,
                             chart_data=chart_data,
                             date_wise_attendance=date_wise_attendance)
    
    # Global camera variable
    camera = None
    camera_lock = threading.Lock()
    
    # Global face encodings cache
    known_face_encodings = []
    known_student_ids = []
    known_student_names = []
    encodings_lock = threading.Lock()
    recognized_today = set()  # Track students recognized today
    
    def load_face_encodings():
        """Load all face encodings from database"""
        if not FACE_RECOGNITION_AVAILABLE:
            print("Face recognition not available - skipping encoding load")
            return
        
        global known_face_encodings, known_student_ids, known_student_names
        with encodings_lock:
            encodings_dict = get_all_face_encodings()
            known_face_encodings = []
            known_student_ids = []
            known_student_names = []
            
            for student_id, (encoding, name) in encodings_dict.items():
                known_face_encodings.append(encoding)
                known_student_ids.append(student_id)
                known_student_names.append(name)
            
            print(f"Loaded {len(known_face_encodings)} face encodings")
    
    # Load face encodings on startup (if available)
    if FACE_RECOGNITION_AVAILABLE:
        load_face_encodings()
    
    def get_camera():
        """Get or create camera instance with error handling"""
        global camera
        with camera_lock:
            if camera is None:
                try:
                    camera = cv2.VideoCapture(0)
                    if not camera.isOpened():
                        raise Exception("Camera not accessible")
                    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                except Exception as e:
                    print(f"Camera error: {e}")
                    camera = None
                    raise
            return camera
    
    def release_camera():
        """Release camera resource"""
        global camera
        with camera_lock:
            if camera is not None:
                camera.release()
                camera = None
    
    def generate_frames():
        """Video streaming generator function with face recognition"""
        try:
            camera = get_camera()
        except Exception as e:
            # Return error frame
            error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(error_frame, "Camera Error", (200, 200), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(error_frame, "Please check camera connection", (100, 250), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            ret, buffer = cv2.imencode('.jpg', error_frame)
            if ret:
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            return
        
        process_this_frame = True
        tolerance = 0.6  # Lower is more strict (0.6 is default)
        error_count = 0
        max_errors = 10
        
        while True:
            try:
                success, frame = camera.read()
                if not success:
                    error_count += 1
                    if error_count > max_errors:
                        break
                    continue
                error_count = 0  # Reset on success
            except Exception as e:
                print(f"Camera read error: {e}")
                error_count += 1
                if error_count > max_errors:
                    break
                continue
            
            # Resize frame for faster processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            # Process every other frame to save processing time
            if process_this_frame:
                # Find all faces and face encodings in the current frame
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                
                face_names = []
                face_confidences = []
                face_student_ids = []
                
                for face_encoding in face_encodings:
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(
                        known_face_encodings, face_encoding, tolerance=tolerance)
                    face_distances = face_recognition.face_distance(
                        known_face_encodings, face_encoding)
                    
                    best_match_index = np.argmin(face_distances)
                    
                    if matches[best_match_index] and face_distances[best_match_index] < tolerance:
                        name = known_student_names[best_match_index]
                        student_id = known_student_ids[best_match_index]
                        confidence = 1 - face_distances[best_match_index]
                        
                        face_names.append(name)
                        face_confidences.append(confidence)
                        face_student_ids.append(student_id)
                        
                        # Mark attendance if not already marked today (prevent duplicates)
                        today_key = f"{student_id}_{date.today()}"
                        if today_key not in recognized_today:
                            # Check database to ensure not already marked
                            if not check_attendance_today(student_id):
                                # Mark attendance
                                attendance_id = mark_attendance(
                                    student_id=student_id,
                                    method='face_recognition',
                                    confidence_score=float(confidence)
                                )
                                if attendance_id:
                                    recognized_today.add(today_key)
                                    print(f"Attendance marked for {name} (ID: {student_id}) with confidence: {confidence:.2f}")
                            else:
                                # Already marked today - add to cache to prevent repeated checks
                                recognized_today.add(today_key)
                    else:
                        face_names.append("Unknown")
                        face_confidences.append(0.0)
                        face_student_ids.append(None)
            
            process_this_frame = not process_this_frame
            
            # Display the results
            for (top, right, bottom, left), name, confidence, student_id in zip(face_locations, face_names, face_confidences, face_student_ids):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4
                
                # Draw a box around the face
                if name != "Unknown" and student_id:
                    color = (0, 255, 0)  # Green for recognized
                    # Mark attendance indicator
                    today_key = f"{student_id}_{date.today()}"
                    if today_key in recognized_today:
                        label = f"{name} (Attendance Marked)"
                    else:
                        label = f"{name} ({confidence:.2f})"
                else:
                    color = (0, 0, 255)  # Red for unknown
                    label = "Unknown"
                
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                
                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, label, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)
            
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            frame_bytes = buffer.tobytes()
            # Yield frame in byte format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    @app.route('/video_feed')
    def video_feed():
        """Video streaming route"""
        return Response(generate_frames(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    
    @app.route('/take_attendance')
    def take_attendance():
        """Take attendance page with camera feed"""
        # Reload face encodings in case new students were added
        load_face_encodings()
        # Reset recognized_today at start of new day (simple check)
        today = date.today()
        if not hasattr(app, 'last_check_date') or app.last_check_date != today:
            recognized_today.clear()
        app.last_check_date = today
        return render_template('take_attendance.html')
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """Register a new student"""
        if request.method == 'POST':
            # Get form data
            student_id = request.form.get('student_id', '').strip()
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            
            # Validate required fields
            if not student_id or not name or not email:
                flash('All fields are required', 'error')
                return render_template('register.html')
            
            # Input validation
            if not validate_student_id(student_id):
                flash('Invalid student ID. Student ID must be between 1 and 50 characters.', 'error')
                return render_template('register.html')
            
            if not validate_name(name):
                flash('Invalid name. Name must be between 2 and 100 characters.', 'error')
                return render_template('register.html')
            
            if not validate_email(email):
                flash('Invalid email format. Please enter a valid email address.', 'error')
                return render_template('register.html')
            
            # Check if file is present
            if 'face_image' not in request.files:
                flash('Face image is required', 'error')
                return render_template('register.html')
            
            file = request.files['face_image']
            
            # Check if file is selected
            if file.filename == '':
                flash('No file selected', 'error')
                return render_template('register.html')
            
            # Validate file
            if not allowed_file(file.filename):
                flash('Invalid file type. Allowed: PNG, JPG, JPEG, GIF', 'error')
                return render_template('register.html')
            
            try:
                # Save image file temporarily to process it
                # Get file extension
                file_ext = file.filename.rsplit('.', 1)[1].lower()
                # Create secure filename using student_id
                filename = f"{student_id}.{file_ext}"
                filename = secure_filename(filename)
                
                # Save file to faces directory
                file_path = faces_dir / filename
                file.save(str(file_path))
                
                # Load and process image for face recognition
                if not FACE_RECOGNITION_AVAILABLE:
                    flash('Face recognition library not available. Please install dlib and face-recognition. Image saved but encoding not extracted.', 'warning')
                    # Add student without face encoding
                    student_db_id = add_student(student_id, name, email, course=None, face_encoding=None)
                    if student_db_id is None:
                        os.remove(str(file_path))
                        flash('Error: Student ID or Email already exists', 'error')
                        return render_template('register.html')
                    flash(f'Student {name} registered successfully! (Face recognition disabled - install dlib to enable)', 'success')
                    return redirect(url_for('register'))
                
                try:
                    # Load image using face_recognition library
                    image = face_recognition.load_image_file(str(file_path))
                    
                    # Find face locations in the image
                    face_locations = face_recognition.face_locations(image)
                    
                    if len(face_locations) == 0:
                        # No face detected - remove saved image and show error
                        os.remove(str(file_path))
                        flash('No face detected in the image. Please upload a clear front-facing photo.', 'error')
                        return render_template('register.html')
                    
                    if len(face_locations) > 1:
                        # Multiple faces detected - remove saved image and show error
                        os.remove(str(file_path))
                        flash('Multiple faces detected. Please upload an image with only one person.', 'error')
                        return render_template('register.html')
                    
                    # Extract face encoding
                    face_encodings = face_recognition.face_encodings(image, face_locations)
                    
                    if len(face_encodings) == 0:
                        # Face detected but encoding failed
                        os.remove(str(file_path))
                        flash('Unable to generate face encoding. Please try a different image.', 'error')
                        return render_template('register.html')
                    
                    # Get the first (and only) face encoding
                    face_encoding = face_encodings[0]
                    
                except Exception as e:
                    # Error processing image - remove saved file
                    if os.path.exists(str(file_path)):
                        os.remove(str(file_path))
                    flash(f'Error processing image: {str(e)}', 'error')
                    return render_template('register.html')
                
                # Add student to database with face encoding
                student_db_id = add_student(student_id, name, email, course=None, face_encoding=face_encoding)
                
                if student_db_id is None:
                    # Database error - remove saved image
                    if os.path.exists(str(file_path)):
                        os.remove(str(file_path))
                    flash('Error: Student ID or Email already exists', 'error')
                    return render_template('register.html')
                
                flash(f'Student {name} registered successfully with face recognition!', 'success')
                return redirect(url_for('register'))
                
            except Exception as e:
                # Clean up saved file if it exists
                try:
                    file_ext = file.filename.rsplit('.', 1)[1].lower()
                    filename = secure_filename(f"{student_id}.{file_ext}")
                    file_path = faces_dir / filename
                    if os.path.exists(str(file_path)):
                        os.remove(str(file_path))
                except:
                    pass  # File cleanup failed, continue with error message
                flash(f'Error registering student: {str(e)}', 'error')
                return render_template('register.html')
        
        # GET request - show registration form
        return render_template('register.html')
    
    @app.route('/attendance_records')
    @login_required
    def attendance_records():
        """Display attendance records with filtering"""
        # Get filter parameters
        date_filter = request.args.get('date', '').strip()
        student_filter = request.args.get('student', '').strip()
        
        # Get all students for dropdown
        students = get_all_students()
        
        # Get attendance records with filters
        records = get_all_attendance_records(
            student_id_filter=student_filter if student_filter else None,
            date_filter=date_filter if date_filter else None
        )
        
        # Calculate statistics
        total_records = len(records)
        present_count = sum(1 for r in records if r.get('status') == 'present')
        face_recognition_count = sum(1 for r in records if r.get('method') == 'face_recognition')
        
        return render_template('attendance_records.html', 
                             records=records,
                             students=students,
                             date_filter=date_filter,
                             student_filter=student_filter,
                             total_records=total_records,
                             present_count=present_count,
                             face_recognition_count=face_recognition_count)
    
    @app.route('/export_attendance')
    @login_required
    def export_attendance():
        """Export attendance records to CSV"""
        # Get filter parameters
        date_filter = request.args.get('date', '').strip()
        student_filter = request.args.get('student', '').strip()
        
        # Get attendance records with filters
        records = get_all_attendance_records(
            student_id_filter=student_filter if student_filter else None,
            date_filter=date_filter if date_filter else None
        )
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'ID', 'Student ID', 'Name', 'Email', 'Course', 
            'Date', 'Time', 'Status', 'Method', 'Confidence Score', 'Created At'
        ])
        
        # Write data
        for record in records:
            writer.writerow([
                record['id'],
                record['student_identifier'],
                record['name'],
                record['email'],
                record['course'] or '',
                record['date'],
                record['time'],
                record['status'],
                record['method'],
                f"{record['confidence_score']:.4f}" if record['confidence_score'] else '',
                record['created_at']
            ])
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=attendance_records_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return response
    
    @app.route('/students')
    @login_required
    def students():
        """Display all students"""
        students_list = get_all_students()
        # Count students with face encoding
        face_count = sum(1 for s in students_list if s.get('face_encoding') is not None)
        return render_template('students.html', students=students_list, face_count=face_count)
    
    @app.route('/edit_student/<student_id>', methods=['GET', 'POST'])
    @login_required
    def edit_student(student_id):
        """Edit student information and retake face image"""
        student = get_student_by_student_id(student_id)
        
        if not student:
            flash('Student not found', 'error')
            return redirect(url_for('students'))
        
        if request.method == 'POST':
            # Get form data
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            course = request.form.get('course', '').strip() or None
            
            # Input validation
            if not name or not email:
                flash('Name and email are required', 'error')
                return render_template('edit_student.html', student=student)
            
            if not validate_name(name):
                flash('Invalid name. Name must be between 2 and 100 characters.', 'error')
                return render_template('edit_student.html', student=student)
            
            if not validate_email(email):
                flash('Invalid email format. Please enter a valid email address.', 'error')
                return render_template('edit_student.html', student=student)
            
            # Check if new face image is uploaded
            face_image_updated = False
            face_encoding = None
            
            if 'face_image' in request.files:
                file = request.files['face_image']
                
                if file and file.filename != '':
                    # Validate file
                    if allowed_file(file.filename):
                        if not FACE_RECOGNITION_AVAILABLE:
                            flash('Face recognition library not available. Please install dlib and face-recognition to update face encoding.', 'warning')
                        else:
                            try:
                                # Save image temporarily
                                file_ext = file.filename.rsplit('.', 1)[1].lower()
                                filename = f"{student_id}_temp.{file_ext}"
                                temp_path = faces_dir / secure_filename(filename)
                                file.save(str(temp_path))
                                
                                # Process image for face recognition
                                image = face_recognition.load_image_file(str(temp_path))
                                face_locations = face_recognition.face_locations(image)
                                
                                if len(face_locations) == 0:
                                    os.remove(str(temp_path))
                                    flash('No face detected in the image. Please upload a clear front-facing photo.', 'error')
                                    return render_template('edit_student.html', student=student)
                                
                                if len(face_locations) > 1:
                                    os.remove(str(temp_path))
                                    flash('Multiple faces detected. Please upload an image with only one person.', 'error')
                                    return render_template('edit_student.html', student=student)
                                
                                # Extract face encoding
                                face_encodings = face_recognition.face_encodings(image, face_locations)
                                
                                if len(face_encodings) == 0:
                                    os.remove(str(temp_path))
                                    flash('Unable to generate face encoding. Please try a different image.', 'error')
                                    return render_template('edit_student.html', student=student)
                                
                                face_encoding = face_encodings[0]
                                
                                # Save new image (replace old one)
                                final_filename = f"{student_id}.{file_ext}"
                                final_path = faces_dir / secure_filename(final_filename)
                                
                                # Remove old image if exists
                                for ext in ['jpg', 'jpeg', 'png', 'gif']:
                                    old_path = faces_dir / secure_filename(f"{student_id}.{ext}")
                                    if os.path.exists(str(old_path)):
                                        os.remove(str(old_path))
                                
                                # Move temp to final
                                os.rename(str(temp_path), str(final_path))
                                face_image_updated = True
                                
                            except Exception as e:
                                if os.path.exists(str(temp_path)):
                                    os.remove(str(temp_path))
                                flash(f'Error processing image: {str(e)}', 'error')
                                return render_template('edit_student.html', student=student)
                    else:
                        flash('Invalid file type. Allowed: PNG, JPG, JPEG, GIF', 'error')
                        return render_template('edit_student.html', student=student)
            
            # Update student information
            success = update_student(student_id, name=name, email=email, course=course)
            
            if not success:
                flash('Error updating student information. Email might already be in use.', 'error')
                return render_template('edit_student.html', student=student)
            
            # Update face encoding if new image was uploaded
            if face_image_updated and face_encoding is not None:
                update_success = update_face_encoding(student_id, face_encoding)
                if update_success:
                    # Reload face encodings cache
                    load_face_encodings()
                    flash('Student information and face image updated successfully!', 'success')
                else:
                    flash('Student information updated, but face encoding update failed.', 'warning')
            else:
                flash('Student information updated successfully!', 'success')
            
            return redirect(url_for('students'))
        
        # GET request - show edit form
        return render_template('edit_student.html', student=student)
    
    @app.route('/delete_student/<student_id>', methods=['POST'])
    @login_required
    def delete_student_route(student_id):
        """Delete a student"""
        # Check if student exists
        student = get_student_by_student_id(student_id)
        if not student:
            flash('Student not found', 'error')
            return redirect(url_for('students'))
        
        # Delete student
        success = delete_student(student_id)
        
        if success:
            # Delete face image file
            for ext in ['jpg', 'jpeg', 'png', 'gif']:
                face_path = faces_dir / secure_filename(f"{student_id}.{ext}")
                if os.path.exists(str(face_path)):
                    os.remove(str(face_path))
            
            # Reload face encodings cache
            load_face_encodings()
            flash(f'Student {student_id} deleted successfully', 'success')
        else:
            flash('Error deleting student', 'error')
        
        return redirect(url_for('students'))
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
