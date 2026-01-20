
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
    initial_sidebar_state="expanded"
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

# --- Authentication Pages ---
def login_page():
    st.markdown("<h1 style='text-align: center;'>🔐 Login</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if username == Config.ADMIN_USERNAME and password == Config.ADMIN_PASSWORD:
                    st.session_state.logged_in = True
                    st.session_state.user = username
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")

# --- Application Pages ---

def dashboard_page():
    st.title("📊 Dashboard")
    
    # Key Metrics
    col1, col2, col3 = st.columns(3)
    
    # 1. Total Students
    students = get_all_students()
    total_students = len(students)
    col1.metric("Total Students", total_students)
    
    # 2. Present Today
    today_records = get_attendance_by_date(date.today().isoformat())
    present_today = len(today_records)
    col2.metric("Present Today", present_today)
    
    # 3. Attendance Rate
    rate = (present_today / total_students * 100) if total_students > 0 else 0
    col3.metric("Attendance Rate", f"{rate:.1f}%")
    
    st.divider()
    
    # Charts
    col_chart, col_recent = st.columns([2, 1])
    
    with col_chart:
        st.subheader("Attendance Trend (Last 30 Days)")
        end_date = date.today()
        start_date = end_date - timedelta(days=29)
        trend_data = get_attendance_by_date_range(start_date, end_date, limit=30)
        
        if trend_data:
            df_trend = pd.DataFrame(trend_data)
            df_trend['date'] = pd.to_datetime(df_trend['date'])
            df_trend = df_trend.sort_values('date')
            st.bar_chart(df_trend, x='date', y='count')
        else:
            st.info("No attendance data available for the chart.")
            
    with col_recent:
        st.subheader("Recent Activity")
        recent_records = get_all_attendance_records(limit=10)
        if recent_records:
            for record in recent_records:
                st.text(f"{record['time']} - {record['name']}")
                st.caption(f"Status: {record['status']}")
        else:
            st.info("No recent activity.")

def register_student_page():
    st.title("👤 Register Student")
    st.info("Please fill in the details and capture a face image.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        with st.form("register_form"):
            student_id = st.text_input("Student ID (Unique)")
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            course = st.text_input("Course")
            submitted = st.form_submit_button("Submit Details")
            
            if submitted:
                if not student_id or not name or not email:
                    st.error("All fields (ID, Name, Email) are required.")
                elif 'captured_image_path' not in st.session_state:
                    st.error("Please capture a face image first.")
                else:
                    # Retrieve the captured image encoding
                    try:
                        # We need to re-load to catch encoding if it wasn't processed in the other column...
                        # Actually, better to process everything here.
                        pass
                    except Exception as e:
                        st.error(f"Error: {e}")

    with col2:
        st.subheader("Face Capture")
        picture = st.camera_input("Take a picture")
        
        if picture:
            # Process the image immediately to verify face
            try:
                import face_recognition
                
                # Convert to numpy array
                bytes_data = picture.getvalue()
                # Determine file extension (Streamlit camera usually gives jpg)
                
                # Save temporarily to verify
                temp_filename = f"temp_{int(time.time())}.jpg"
                temp_path = Config.FACES_FOLDER / temp_filename
                
                with open(temp_path, "wb") as f:
                    f.write(bytes_data)
                
                # Load and check face
                image = face_recognition.load_image_file(str(temp_path))
                face_locations = face_recognition.face_locations(image)
                
                if len(face_locations) == 0:
                    st.error("No face detected! Please try again.")
                    if os.path.exists(temp_path): os.remove(temp_path)
                elif len(face_locations) > 1:
                    st.error("Multiple faces detected! Please ensure only one person is in frame.")
                    if os.path.exists(temp_path): os.remove(temp_path)
                else:
                    # Valid face
                    st.success("Face detected successfully!")
                    st.session_state['captured_image_bytes'] = bytes_data
                    st.image(picture, caption="Captured Image", width=200)
                    
                    # Clean up temp
                    if os.path.exists(temp_path): os.remove(temp_path)
                    
            except ImportError:
                st.warning("Face recognition library not installed. Cannot verify face.")
            except Exception as e:
                st.error(f"Error processing image: {e}")

    # Handling final submission outside the form to access session state easier
    if submitted and 'captured_image_bytes' in st.session_state and student_id and name:
        try:
            import face_recognition
            
            # Save final image
            filename = f"{student_id}.jpg"
            final_path = Config.FACES_FOLDER / filename
            
            with open(final_path, "wb") as f:
                f.write(st.session_state['captured_image_bytes'])
            
            # Get encoding
            image = face_recognition.load_image_file(str(final_path))
            encodings = face_recognition.face_encodings(image)
            
            if encodings:
                face_encoding = encodings[0]
                
                # Save to DB
                student_db_id = add_student(student_id, name, email, course, face_encoding)
                
                if student_db_id:
                    st.success(f"Student {name} registered successfully!")
                    # Clear session state
                    del st.session_state['captured_image_bytes']
                else:
                    st.error("Error saving to database. ID or Email might duplicate.")
            else:
                st.error("Could not encode face. Try again.")
                
        except Exception as e:
            st.error(f"Registration failed: {e}")

def take_attendance_page():
    st.title("📸 Take Attendance")
    
    run_camera = st.checkbox("Start Camera", value=False)
    
    if run_camera:
        # We use a placeholder to update the video frame
        stframe = st.empty()
        
        # Load known faces
        try:
            encodings_dict = get_all_face_encodings()
            known_face_encodings = [enc[0] for enc in encodings_dict.values()]
            known_student_ids = list(encodings_dict.keys())
            known_names = [enc[1] for enc in encodings_dict.values()]
        except Exception as e:
            st.error(f"Error loading faces: {e}")
            return

        import face_recognition

        video = cv2.VideoCapture(0)
        
        if not video.isOpened():
            st.error("Could not access camera.")
            return

        stop_button = st.button("Stop")
        
        while run_camera and not stop_button:
            ret, frame = video.read()
            if not ret:
                st.error("Failed to read user camera.")
                break
            
            # Resize for speed
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            
            face_names = []
            
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
                name = "Unknown"
                confidence = 0.0
                
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_names[best_match_index]
                        student_id = known_student_ids[best_match_index]
                        confidence = 1 - face_distances[best_match_index]
                        
                        # Mark Attendance
                        if not check_attendance_today(student_id):
                            mark_attendance(student_id, confidence_score=confidence)
                            # Could add toast notification here but might spam
                
                face_names.append(f"{name} ({confidence:.2f})" if name != "Unknown" else name)

            # Draw boxes (optional - for visualization on the Streamlit UI)
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4
                
                color = (0, 255, 0) if "Unknown" not in name else (0, 0, 255)
                
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

            # Display in Streamlit
            stframe.image(frame, channels="BGR")
            
            # Slight delay to reduce CPU usage
            # time.sleep(0.1) 
        
        video.release()

def view_records_page():
    st.title("📋 Attendance Records")
    
    col1, col2 = st.columns(2)
    with col1:
        date_sel = st.date_input("Filter by Date", value=None)
    with col2:
        students = get_all_students()
        student_opts = {s['student_id']: s['name'] for s in students}
        student_sel = st.selectbox("Filter by Student", ["All"] + list(student_opts.keys()), format_func=lambda x: f"{x} - {student_opts[x]}" if x != "All" else "All Students")
    
    # Process filters
    d_filter = date_sel.isoformat() if date_sel else None
    s_filter = student_sel if student_sel != "All" else None
    
    records = get_all_attendance_records(student_id_filter=s_filter, date_filter=d_filter)
    
    if records:
        df = pd.DataFrame(records)
        # Select useful columns
        display_df = df[['date', 'time', 'student_identifier', 'name', 'status', 'confidence_score']]
        st.dataframe(display_df, use_container_width=True)
        
        # CVS Download
        csv = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Download CSV",
            csv,
            "attendance_records.csv",
            "text/csv",
            key='download-csv'
        )
    else:
        st.info("No records found matching filters.")

def manage_students_page():
    st.title("🎓 Manage Students")
    
    students = get_all_students()
    
    if students:
        for student in students:
            with st.expander(f"{student['name']} ({student['student_id']})"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Email:** {student['email']}")
                    st.write(f"**Course:** {student['course']}")
                    st.write(f"**Registered:** {student['created_at']}")
                with col2:
                    if st.button("Delete Student", key=f"del_{student['student_id']}"):
                        if delete_student(student['student_id']):
                            st.success(f"Deleted {student['name']}")
                            st.rerun()
                        else:
                            st.error("Failed to delete.")
    else:
        st.info("No students registered.")

# --- Main Navigation ---

if not st.session_state.logged_in:
    login_page()
else:
    with st.sidebar:
        st.title("Valid Check")
        st.write(f"Logged in as: **{st.session_state.user}**")
        
        page = st.radio("Navigation", [
            "Dashboard", 
            "Register Student", 
            "Take Attendance", 
            "View Records", 
            "Manage Students"
        ])
        
        st.divider()
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    # Routing
    if page == "Dashboard":
        dashboard_page()
    elif page == "Register Student":
        register_student_page()
    elif page == "Take Attendance":
        take_attendance_page()
    elif page == "View Records":
        view_records_page()
    elif page == "Manage Students":
        manage_students_page()
