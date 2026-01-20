
import streamlit as st
import pandas as pd
import numpy as np
import cv2
import time
from datetime import datetime, date, timedelta
from pathlib import Path
import os
import pickle

# Import models and config
from models.student_model import (
    create_tables, add_student, get_all_students, 
    mark_attendance, check_attendance_today, 
    get_all_attendance_records, get_attendance_by_date, 
    get_attendance_by_date_range, get_all_face_encodings,
    delete_student
)
from config import Config

# --- Configuration & Setup ---
st.set_page_config(
    page_title="Attendance System",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="collapsed" # Collapsed to mimic the "web app" feel more, or expanded if navbar is needed
)

# Ensure database tables exist
try:
    create_tables()
except Exception as e:
    st.error(f"Database initialization error: {e}")

# Ensure static directories exist
os.makedirs(Config.FACES_FOLDER, exist_ok=True)
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

# --- Session State Management ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None

# --- Custom CSS & Assets ---
def load_css():
    st.markdown("""
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;600;700&display=swap');
            
            /* Global Reset & Font */
            html, body, [class*="css"] {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f5f5f5;
                color: #333;
            }
            
            /* --- Common Components --- */
            
            /* Page Headers */
            .page-header {
                text-align: center;
                margin-bottom: 2rem;
            }
            .page-header h1 {
                color: #212529;
                font-weight: 700;
                margin-bottom: 0.5rem;
                font-size: 2rem;
            }
            .page-header p {
                color: #6c757d;
            }
            
            /* Cards */
            .card-common {
                background: white;
                border-radius: 12px;
                padding: 1.5rem;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                margin-bottom: 1.5rem;
            }
            
            /* Stat Cards */
            .stat-card {
                background: white;
                border-radius: 12px;
                padding: 1.5rem;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                transition: transform 0.3s, box-shadow 0.3s;
                border-left: 4px solid #0d6efd;
                height: 100%;
                text-align: center;
            }
            .stat-card:hover { transform: translateY(-3px); }
            .stat-card.success { border-left-color: #28a745; }
            .stat-card.warning { border-left-color: #ffc107; }
            .stat-card.info { border-left-color: #17a2b8; }
            
            .stat-icon {
                font-size: 2.5rem;
                color: #0d6efd;
                margin-bottom: 1rem;
            }
            .stat-card.success .stat-icon { color: #28a745; }
            .stat-card.warning .stat-icon { color: #ffc107; }
            
            .stat-card h4, .stat-card .stat-number {
                font-size: 2rem;
                font-weight: 700;
                color: #212529;
                margin-bottom: 0;
            }
            .stat-card p, .stat-card h5 {
                color: #6c757d;
                font-size: 0.9rem;
                font-weight: 600;
                text-transform: uppercase;
                margin-bottom: 0.5rem;
            }
            
            /* Tables */
            .custom-table {
                width: 100%;
                border-collapse: collapse;
                background: white;
                border-radius: 8px;
                overflow: hidden;
            }
            .custom-table th {
                background: linear-gradient(135deg, #0d6efd 0%, #0a58ca 100%);
                color: white;
                padding: 1rem;
                text-align: left;
                font-weight: 600;
            }
            .custom-table td {
                padding: 1rem;
                border-bottom: 1px solid #e9ecef;
                vertical-align: middle;
            }
            .custom-table tr:hover { background-color: #f8f9fa; }
            
            /* Badges */
            .badge {
                padding: 0.35rem 0.65rem;
                border-radius: 0.25rem;
                font-weight: 700;
                font-size: 0.75rem;
                color: white;
                display: inline-block;
            }
            .badge-success { background-color: #28a745; }
            .badge-danger { background-color: #dc3545; }
            .badge-warning { background-color: #ffc107; color: #212529; }
            .badge-info { background-color: #17a2b8; }
            .badge-secondary { background-color: #6c757d; }
            .badge-face { background-color: #17a2b8; }
            .badge-no-face { background-color: #6c757d; }
            
            .confidence-score { color: #28a745; font-weight: 600; }
            
            /* Avatars */
            .student-avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                object-fit: cover;
                border: 2px solid #dee2e6;
                vertical-align: middle;
            }
            
            /* Input Styling Override (Best Effort) */
            div[data-testid="stTextInput"] > div > div > input {
                border-radius: 8px;
            }
            
            /* Hide Streamlit Elements */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            .stDeployButton {display:none;}
            
            /* Specific Page Styles */
            .login-container { max-width: 450px; margin: 0 auto; padding-top: 5rem; }
            
            /* Navigation */
            div[data-testid="stSidebarNav"] {
                padding-top: 1rem;
            }
        </style>
    """, unsafe_allow_html=True)

load_css()

# --- Helper Functions ---
def render_header(title, subtitle, icon):
    st.markdown(f"""
        <div class="page-header">
            <h1><i class="bi {icon} me-2"></i>{title}</h1>
            <p>{subtitle}</p>
        </div>
    """, unsafe_allow_html=True)

# --- Pages ---

def login_page():
    # Use columns to center the login form, mimicking .login-container
    c1, c2, c3 = st.columns([1, 1, 1])
    
    with c2:
        st.markdown("""
            <div class="page-header" style="margin-bottom: 1rem;">
                <i class="bi bi-shield-lock" style="font-size: 4rem; color: #0d6efd;"></i>
                <h1>Admin Login</h1>
                <p>Access the admin dashboard</p>
            </div>
            <div class="card-common">
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown('<label class="form-label" style="font-weight:600;">Username</label>', unsafe_allow_html=True)
            username = st.text_input("Username", label_visibility="collapsed", placeholder="Enter username")
            
            st.markdown('<label class="form-label" style="font-weight:600; margin-top:1rem;">Password</label>', unsafe_allow_html=True)
            password = st.text_input("Password", type="password", label_visibility="collapsed", placeholder="Enter password")
            
            st.markdown('<br>', unsafe_allow_html=True)
            submit = st.form_submit_button("Login", use_container_width=True, type="primary")
            
            if submit:
                if username == Config.ADMIN_USERNAME and password == Config.ADMIN_PASSWORD:
                    st.session_state.logged_in = True
                    st.session_state.user = username
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        
        st.markdown("""
            </div>
            <div style="background: #e7f1ff; border-left: 4px solid #0d6efd; padding: 1rem; border-radius: 8px; margin-top: 1rem; font-size: 0.9rem;">
                <strong>Default Credentials:</strong><br>
                Username: <code>admin</code><br>
                Password: <code>admin123</code>
            </div>
        """, unsafe_allow_html=True)

def dashboard_page():
    render_header("Admin Dashboard", "Monitor and manage student attendance in real-time", "bi-speedometer2")
    
    students = get_all_students()
    total_students = len(students)
    today_records = get_attendance_by_date(date.today().isoformat())
    present_today = len(today_records)
    attendance_rate = (present_today / total_students * 100) if total_students > 0 else 0
    
    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="stat-card"><div class="stat-icon"><i class="bi bi-people-fill"></i></div><h5>Total Students</h5><p class="stat-number">{total_students}</p></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="stat-card success"><div class="stat-icon"><i class="bi bi-calendar-check-fill"></i></div><h5>Today\'s Attendance</h5><p class="stat-number">{present_today}</p></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="stat-card warning"><div class="stat-icon"><i class="bi bi-graph-up-arrow"></i></div><h5>Attendance Rate</h5><p class="stat-number">{attendance_rate:.1f}%</p></div>', unsafe_allow_html=True)
    
    # Chart
    st.markdown('<div class="card-common" style="margin-top:2rem;"><h2><i class="bi bi-bar-chart-fill me-2"></i>Date-wise Attendance (Last 30 Days)</h2>', unsafe_allow_html=True)
    end_date = date.today()
    start_date = end_date - timedelta(days=29)
    trend_data = get_attendance_by_date_range(start_date, end_date, limit=30)
    
    if trend_data:
        df_trend = pd.DataFrame(trend_data)
        df_trend['date'] = pd.to_datetime(df_trend['date'])
        df_trend = df_trend.sort_values('date').set_index('date')
        st.area_chart(df_trend['count'], color="#0d6efd", height=300)
    else:
        st.info("No attendance data available for the chart.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Recent Records
    st.markdown('<div class="card-common">', unsafe_allow_html=True)
    st.markdown('<h2><i class="bi bi-clock-history me-2"></i>Recent Attendance Records</h2>', unsafe_allow_html=True)
    
    recent_records = get_all_attendance_records(limit=10)
    if recent_records:
        render_records_table(recent_records)
    else:
        st.markdown('<div style="text-align: center; padding: 2rem;"><i class="bi bi-inbox" style="font-size: 3rem; opacity: 0.5;"></i><p>No records found.</p></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick Actions
    c1, c2 = st.columns(2)
    c1.markdown('<div class="card-common" style="cursor:pointer;"><h5 style="color:#212529; font-size:1.2rem;"><i class="bi bi-camera-fill me-2" style="color:#0d6efd;"></i>Take Attendance</h5><p style="color:#6c757d;">Use face recognition to mark attendance.</p></div>', unsafe_allow_html=True)
    c2.markdown('<div class="card-common" style="cursor:pointer;"><h5 style="color:#212529; font-size:1.2rem;"><i class="bi bi-person-plus-fill me-2" style="color:#0d6efd;"></i>Register New Student</h5><p style="color:#6c757d;">Add a new student to the system.</p></div>', unsafe_allow_html=True)

def register_student_page():
    render_header("Register New Student", "Add a new student to the attendance system", "bi-person-plus-fill")
    
    c_main = st.container()
    
    with c_main:
        c1, c2 = st.columns([1, 1], gap="large")
        
        with c1:
            st.markdown('<div class="card-common"><h3>Student Details</h3>', unsafe_allow_html=True)
            with st.form("reg_form"):
                st.markdown('<label class="form-label">Student ID <span style="color:red">*</span></label>', unsafe_allow_html=True)
                student_id = st.text_input("ID", label_visibility="collapsed", placeholder="e.g., STU001")
                
                st.markdown('<label class="form-label">Full Name <span style="color:red">*</span></label>', unsafe_allow_html=True)
                name = st.text_input("Name", label_visibility="collapsed", placeholder="Enter full name")
                
                st.markdown('<label class="form-label">Email <span style="color:red">*</span></label>', unsafe_allow_html=True)
                email = st.text_input("Email", label_visibility="collapsed", placeholder="student@example.com")
                
                st.markdown('<label class="form-label">Course</label>', unsafe_allow_html=True)
                course = st.text_input("Course", label_visibility="collapsed", placeholder="Enter course name")
                
                st.markdown("<br>", unsafe_allow_html=True)
                submitted = st.form_submit_button("Register Student", type="primary", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with c2:
            st.markdown('<div class="card-common"><h3>Face Capture</h3>', unsafe_allow_html=True)
            st.info("Please capture a clear front-facing photo.")
            picture = st.camera_input("Take a picture")
            
            if picture:
                st.session_state['captured_image_bytes'] = picture.getvalue()
                st.success("Image captured successfully!")
            st.markdown('</div>', unsafe_allow_html=True)

    # Logic
    if submitted:
        if not student_id or not name or not email:
            st.error("Please fill in all required fields.")
        elif 'captured_image_bytes' not in st.session_state:
            st.error("Please capture a face image.")
        else:
            try:
                import face_recognition
                
                # Save temp
                temp_path = Config.FACES_FOLDER / f"temp_{int(time.time())}.jpg"
                with open(temp_path, "wb") as f:
                    f.write(st.session_state['captured_image_bytes'])
                
                # Process
                image = face_recognition.load_image_file(str(temp_path))
                encodings = face_recognition.face_encodings(image)
                
                if len(encodings) > 0:
                    face_encoding = encodings[0]
                    # Save final
                    final_path = Config.FACES_FOLDER / f"{student_id}.jpg"
                    with open(final_path, "wb") as f:
                        f.write(st.session_state['captured_image_bytes'])
                    
                    if os.path.exists(temp_path): os.remove(temp_path)
                    
                    if add_student(student_id, name, email, course, face_encoding):
                        st.success(f"Student {name} registered successfully!")
                        del st.session_state['captured_image_bytes']
                    else:
                        st.error("Error: Student ID or Email already exists.")
                else:
                    st.error("No face detected in the image. Please try again.")
                    if os.path.exists(temp_path): os.remove(temp_path)
                    
            except Exception as e:
                st.error(f"Registration error: {e}")

def take_attendance_page():
    render_header("Take Attendance", "Position yourself in front of the camera", "bi-camera-fill")
    
    col_cam, col_info = st.columns([2, 1])
    
    with col_cam:
        st.markdown('<div class="card-common" style="padding:1rem;">', unsafe_allow_html=True)
        st.markdown('<div style="display:flex; justify-content:space-between; margin-bottom:1rem;"><h3>Camera Feed</h3><span class="badge badge-success">Active</span></div>', unsafe_allow_html=True)
        
        # We need a loop for the camera
        run_camera = st.checkbox("Start Camera Session", value=False)
        stframe = st.empty()
        
        st.markdown('</div>', unsafe_allow_html=True)

    with col_info:
        st.markdown("""
            <div class="card-common">
                <h3>Instructions</h3>
                <div class="alert alert-info" style="background:#e7f1ff; border-left:4px solid #0d6efd; padding:1rem; border-radius:8px; color:#0c5460;">
                    <i class="bi bi-info-circle me-2"></i>Look directly at the camera.
                </div>
                <ul style="list-style:none; padding-left:0; margin-top:1rem;">
                    <li style="margin-bottom:0.5rem;"><i class="bi bi-check-circle text-success me-2"></i>Green Box: Recognized</li>
                    <li style="margin-bottom:0.5rem;"><i class="bi bi-x-circle text-danger me-2"></i>Red Box: Unknown</li>
                    <li><i class="bi bi-clock me-2"></i>Auto-marks once per day</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        
        msg_placeholder = st.empty()

    if run_camera:
        try:
            encodings_dict = get_all_face_encodings()
            known_face_encodings = [enc[0] for enc in encodings_dict.values()]
            known_student_ids = list(encodings_dict.keys())
            known_names = [enc[1] for enc in encodings_dict.values()]
            
            video = cv2.VideoCapture(0)
            
            while run_camera:
                ret, frame = video.read()
                if not ret:
                    st.error("Failed to access camera.")
                    break
                
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                
                faces_found = []
                
                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
                    name = "Unknown"
                    confidence = 0.0
                    
                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                    if len(face_distances) > 0:
                        best_match_index = np.argmin(face_distances)
                        if matches[best_match_index]:
                            name = known_names[best_match_index]
                            student_id = known_student_ids[best_match_index]
                            confidence = 1 - face_distances[best_match_index]
                            
                            # Mark Attendance Logic
                            if not check_attendance_today(student_id):
                                mark_attendance(student_id, confidence_score=confidence)
                                msg_placeholder.success(f"Marked attendance for {name}!")
                            else:
                                msg_placeholder.info(f"Attendance already marked for {name}.")
                    
                    faces_found.append((name, confidence))

                # Draw
                for (top, right, bottom, left), (name, conf) in zip(face_locations, faces_found):
                    top *= 4; right *= 4; bottom *= 4; left *= 4
                    color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                    label = f"{name} ({conf:.2f})" if name != "Unknown" else name
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                    cv2.putText(frame, label, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
                
                stframe.image(frame, channels="BGR")
                
            video.release()
        except Exception as e:
            st.error(f"Error initializing camera: {e}")

def view_records_page():
    render_header("Attendance Records", "View and manage student attendance records", "bi-calendar-check")
    
    # Stats
    records = get_all_attendance_records() # Get all initially for stats
    total = len(records)
    present = len([r for r in records if r['status'] == 'present'])
    
    col1, col2, col3 = st.columns(3)
    col1.markdown(f'<div class="stat-card"><div class="stat-icon"><i class="bi bi-list-check"></i></div><h4>{total}</h4><p>Total Records</p></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="stat-card success"><div class="stat-icon"><i class="bi bi-check-circle-fill"></i></div><h4>{present}</h4><p>Present</p></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="stat-card info"><div class="stat-icon"><i class="bi bi-camera-fill"></i></div><h4>{present}</h4><p>Face Recognition</p></div>', unsafe_allow_html=True) # Assuming all present are face rec
    
    # Filters
    st.markdown('<div class="card-common" style="margin-top:2rem;"><h3><i class="bi bi-funnel me-2"></i>Filters</h3>', unsafe_allow_html=True)
    fc1, fc2, fc3 = st.columns([1, 1, 1])
    with fc1:
        d_val = st.date_input("Filter by Date", value=None)
    with fc2:
        students = get_all_students()
        s_opts = {s['student_id']: s['name'] for s in students}
        s_val = st.selectbox("Filter by Student", ["All"] + list(s_opts.keys()), format_func=lambda x: f"{x} - {s_opts[x]}" if x != "All" else "All Students")
    with fc3:
        st.markdown("<br>", unsafe_allow_html=True)
        # Streamlit updates on change, so button mostly just for feeling
        st.button("Apply Filters", type="primary")
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Process Filter
    d_str = d_val.isoformat() if d_val else None
    s_str = s_val if s_val != "All" else None
    filtered_records = get_all_attendance_records(student_id_filter=s_str, date_filter=d_str)
    
    # Table
    st.markdown('<div class="card-common">', unsafe_allow_html=True)
    st.markdown('<h3>Attendance List</h3>', unsafe_allow_html=True)
    if filtered_records:
        render_records_table(filtered_records)
    else:
        st.info("No records match your filters.")
    st.markdown('</div>', unsafe_allow_html=True)

def manage_students_page():
    render_header("Students", "Manage student information and face encodings", "bi-people-fill")
    
    students = get_all_students()
    
    # stats
    c1, c2 = st.columns(2)
    c1.markdown(f'<div class="stat-card"><h4>{len(students)}</h4><p>Total Students</p></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="stat-card success"><h4>{len(students)}</h4><p>With Face Encoding</p></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card-common" style="margin-top:2rem;"><h3>Student List</h3>', unsafe_allow_html=True)
    
    if students:
        # Table Header
        html = '<table class="custom-table"><thead><tr><th>Photo</th><th>ID</th><th>Name</th><th>Email</th><th>Course</th><th>Registered</th><th>Action</th></tr></thead><tbody>'
        
        for s in students:
            # Check for image
            img_path = ""
            for ext in ['jpg', 'png', 'jpeg']:
                p = Config.FACES_FOLDER / f"{s['student_id']}.{ext}"
                if p.exists():
                    img_path = f"app/static/faces/{s['student_id']}.{ext}" # Streamlit static handling is tricky, usually relies on base static
                    # We will use the 'static' folder feature of Streamlit if configured, OR base64 
                    # For now, just a placeholder icon if we can't easily serve the file without complex setup
                    # Actually, Streamlit serves from 'static' folder if placed in root 'static'
                    break
            
            # Since we can't easily get the URL for the local file in standard Streamlit without hosting it specifically, 
            # we'll use a placeholder icon for simplicity or base64 if we really wanted.
            # Visual placeholder:
            avatar = '<i class="bi bi-person-circle" style="font-size:1.5rem; color:#6c757d;"></i>'
            
            html += f"""
                <tr>
                    <td>{avatar}</td>
                    <td><strong>{s['student_id']}</strong></td>
                    <td>{s['name']}</td>
                    <td>{s['email']}</td>
                    <td>{s['course']}</td>
                    <td>{s['created_at'][:10]}</td>
                    <td><span class="badge badge-face">Registered</span></td>
                </tr>
            """
        html += "</tbody></table>"
        st.markdown(html, unsafe_allow_html=True)
        
        # Deletion is tricky inside HTML table. We use a separate expander for actions to be safe and maintain interactivity
        st.markdown("</div>", unsafe_allow_html=True)
        
        with st.expander("Manage / Delete Students"):
            s_to_del = st.selectbox("Select Student to Delete", [s['student_id'] for s in students], format_func=lambda x: f"{x} - {[s['name'] for s in students if s['student_id']==x][0]}")
            if st.button("Delete Selected Student", type="primary"):
                if delete_student(s_to_del):
                    st.success("Student deleted.")
                    st.rerun()
    else:
        st.info("No students registered.")
        st.markdown("</div>", unsafe_allow_html=True)

def render_records_table(records):
    html = '<table class="custom-table"><thead><tr><th>ID</th><th>Name</th><th>Date</th><th>Time</th><th>Status</th><th>Method</th><th>Confidence</th></tr></thead><tbody>'
    for r in records:
        status_cls = "badge-success" if r['status'] == 'present' else "badge-danger" if r['status'] == 'absent' else "badge-warning"
        status_html = f'<span class="badge {status_cls}">{r["status"].title()}</span>'
        
        method_html = f'<span class="badge badge-info"><i class="bi bi-camera-fill me-1"></i>Face Rec</span>' if r['method'] == 'face_recognition' else r['method']
        score = f'<span class="confidence-score">{r["confidence_score"]*100:.1f}%</span>' if r['confidence_score'] else "-"
        
        html += f"""
            <tr>
                <td><strong>{r['student_identifier']}</strong></td>
                <td>{r['name']}</td>
                <td>{r['date']}</td>
                <td>{r['time']}</td>
                <td>{status_html}</td>
                <td>{method_html}</td>
                <td>{score}</td>
            </tr>
        """
    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)

# --- Navigation & Routing ---

if not st.session_state.logged_in:
    login_page()
else:
    # Sidebar
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2922/2922510.png", width=50)
        st.title("Attendance")
        st.markdown(f"User: **{st.session_state.user}**")
        
        menu = st.radio(
            "Navigation", 
            ["Dashboard", "Register Student", "Take Attendance", "View Records", "Manage Students"],
            label_visibility="collapsed"
        )
        
        st.divider()
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
            
    # Route
    if menu == "Dashboard": dashboard_page()
    elif menu == "Register Student": register_student_page()
    elif menu == "Take Attendance": take_attendance_page()
    elif menu == "View Records": view_records_page()
    elif menu == "Manage Students": manage_students_page()
