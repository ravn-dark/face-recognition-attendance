# Automated Attendance System Using Computer Vision

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8.1-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**A comprehensive face recognition-based attendance management system built with Flask and Computer Vision**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Architecture](#-architecture) • [Tech Stack](#-tech-stack)

</div>

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage Guide](#-usage-guide)
- [How Attendance Works](#-how-attendance-works)
- [Project Structure](#-project-structure)
- [Screenshots](#-screenshots)
- [API Endpoints](#-api-endpoints)
- [Database Schema](#-database-schema)
- [Future Scope](#-future-scope)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Project Overview

The **Automated Attendance System Using Computer Vision** is an intelligent attendance management solution that leverages facial recognition technology to automatically track and record student attendance. The system eliminates manual attendance marking, reduces human error, and provides real-time attendance monitoring with comprehensive analytics.

### Key Highlights

- **Automated Recognition**: Real-time face detection and recognition using advanced computer vision algorithms
- **Web-Based Interface**: Modern, responsive web application built with Flask and Bootstrap 5
- **Secure & Reliable**: Admin authentication, input validation, and robust error handling
- **Comprehensive Analytics**: Date-wise attendance tracking with visual charts and statistics
- **Export Capabilities**: CSV export functionality for attendance records
- **Student Management**: Complete CRUD operations for student information and face encodings

---

## ✨ Features

### Core Functionality

- ✅ **Face Recognition-Based Attendance**
  - Real-time camera feed processing
  - Automatic face detection and encoding extraction
  - 128-dimensional face encoding storage
  - Confidence score tracking

- ✅ **Student Management**
  - Student registration with face image upload
  - Edit student information
  - Delete students with cascade attendance deletion
  - Retake face images for recognition updates

- ✅ **Attendance Tracking**
  - Automatic attendance marking on face recognition
  - Duplicate prevention (one attendance per day per student)
  - Date and student-based filtering
  - Real-time attendance statistics

- ✅ **Admin Dashboard**
  - Total students count
  - Today's attendance statistics
  - Attendance rate calculation
  - Date-wise attendance visualization (Chart.js)
  - Recent attendance records table

- ✅ **Data Export**
  - CSV export with filtering support
  - Timestamped file generation
  - Complete attendance data export

### Security & Quality

- 🔐 **Admin Authentication**: Session-based login system
- ✅ **Input Validation**: Email, name, and student ID validation
- 🎥 **Camera Error Handling**: Graceful error handling for camera failures
- 🚫 **Duplicate Prevention**: Database and cache-based duplicate attendance prevention
- 💬 **Flash Messages**: User-friendly success/error notifications

---

## 🛠 Tech Stack

### Backend
- **Python 3.10+**: Core programming language
- **Flask 3.0.0**: Web framework
- **SQLite3**: Lightweight database for data persistence
- **face_recognition 1.3.0**: Face detection and encoding library
- **OpenCV 4.8.1**: Computer vision and image processing
- **NumPy 1.24.3**: Numerical computations for face encodings

### Frontend
- **Bootstrap 5.3.2**: Responsive UI framework
- **Bootstrap Icons**: Icon library
- **Chart.js 4.4.0**: Data visualization for attendance charts
- **HTML5/CSS3/JavaScript**: Modern web technologies

### Database
- **SQLite**: Relational database with BLOB storage for face encodings
- **Pickle**: Serialization for face encoding storage

### Development Tools
- **Werkzeug 3.0.1**: WSGI utilities
- **Pillow 10.1.0**: Image processing

---

## 🏗 Architecture

The system follows a modular architecture with clear separation of concerns:

```
┌─────────────────┐
│   Web Browser   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Flask App      │
│  (Routes/Views) │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐  ┌──────────────┐
│ Models │  │ Face Recog.  │
│ (DB)   │  │ (OpenCV)     │
└────────┘  └──────────────┘
    │
    ▼
┌─────────────┐
│ SQLite DB   │
│ (Students,  │
│ Attendance) │
└─────────────┘
```

### System Flow

1. **Registration**: Student uploads photo → Face detection → Encoding extraction → Database storage
2. **Attendance**: Camera feed → Face detection → Encoding comparison → Attendance marking
3. **Analytics**: Database queries → Data aggregation → Chart visualization

---

## 📦 Installation

### Prerequisites

- Python 3.10 or higher
- Webcam/Camera (for attendance marking)
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd system
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: The `face_recognition` library requires `dlib`, which may need additional system dependencies:

**Windows:**
```bash
pip install dlib
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install cmake libopenblas-dev liblapack-dev
pip install dlib
```

**macOS:**
```bash
brew install cmake
pip install dlib
```

### Step 4: Run the Application

```bash
python app.py
```

The application will be available at: `http://localhost:5000`

### Step 5: Access the System

1. Navigate to `http://localhost:5000` in your web browser
2. Click on **Login** in the navigation bar
3. Use default credentials:
   - **Username**: `admin`
   - **Password**: `admin123`

---

## ⚙️ Configuration

### Environment Variables (Optional)

Create a `.env` file in the project root for production settings:

```env
SECRET_KEY=your-secret-key-here
ADMIN_USERNAME=your-admin-username
ADMIN_PASSWORD=your-secure-password
DATABASE_URL=sqlite:///attendance.db
```

### Default Configuration

The system uses default configuration from `config.py`:
- Database: `attendance.db` (SQLite)
- Face images: `static/faces/`
- Upload limit: 16MB
- Allowed formats: PNG, JPG, JPEG, GIF

---

## 📖 Usage Guide

### 1. Admin Login

1. Navigate to the login page
2. Enter admin credentials
3. Access the dashboard upon successful login

### 2. Register Students

1. Go to **Register Student** from the navigation
2. Fill in student details:
   - Student ID (unique)
   - Full Name
   - Email Address
3. Upload a clear front-facing photo
4. System automatically:
   - Detects face in the image
   - Extracts 128-dimensional encoding
   - Stores encoding in database
5. Student is registered and ready for attendance

### 3. Take Attendance

1. Navigate to **Take Attendance**
2. Camera feed will start automatically
3. Student stands in front of camera
4. System automatically:
   - Detects face in real-time
   - Compares with stored encodings
   - Marks attendance if match found
   - Prevents duplicate marking
5. Visual feedback shows recognition status

### 4. View Records

1. Go to **Attendance Records**
2. Filter by:
   - Date (date picker)
   - Student (dropdown)
3. View all attendance records in table format
4. Export to CSV if needed

### 5. Manage Students

1. Access **Students** page
2. View all registered students
3. Edit student information
4. Retake face images
5. Delete students (with cascade)

---

## 🔄 How Attendance Works

### Face Recognition Pipeline

```
1. Camera Capture
   └─> Live video frame (640x480)

2. Face Detection (OpenCV)
   └─> Face locations in frame

3. Face Encoding (face_recognition)
   └─> 128-dimensional encoding vector

4. Database Comparison
   └─> Compare with stored encodings
   └─> Calculate distance (tolerance: 0.6)

5. Match Found?
   ├─> YES → Check if already marked today
   │   ├─> NO → Mark attendance
   │   └─> YES → Skip (prevent duplicate)
   └─> NO → Display "Unknown"
```

### Technical Details

- **Face Detection**: Uses HOG (Histogram of Oriented Gradients) algorithm
- **Face Encoding**: 128-dimensional vector using deep learning model
- **Matching Algorithm**: Euclidean distance calculation with tolerance threshold
- **Confidence Score**: Calculated as `1 - face_distance`
- **Storage**: Face encodings stored as pickled BLOB in SQLite

### Duplicate Prevention

The system uses a two-layer approach:
1. **In-Memory Cache**: Tracks recognized students for the current day
2. **Database Check**: Verifies attendance record existence before marking

---

## 📁 Project Structure

```
system/
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── .gitignore                  # Git ignore rules
│
├── models/                     # Database models
│   ├── __init__.py
│   ├── database.py            # Database initialization
│   ├── models.py              # SQLAlchemy models (legacy)
│   └── student_model.py       # SQLite models and functions
│
├── templates/                  # HTML templates
│   ├── base.html              # Base template with navbar
│   ├── index.html             # Home page
│   ├── login.html             # Admin login page
│   ├── dashboard.html         # Admin dashboard
│   ├── register.html          # Student registration
│   ├── students.html          # Student management
│   ├── edit_student.html      # Edit student form
│   ├── take_attendance.html   # Camera attendance page
│   └── attendance_records.html # Attendance records
│
└── static/                     # Static files
    ├── css/
    │   └── style.css          # Custom styles
    ├── js/
    │   └── main.js            # JavaScript utilities
    ├── faces/                 # Student face images
    └── uploads/               # General uploads
```

---

## 📸 Screenshots

### Dashboard View
![Dashboard](screenshots/dashboard.png)
*Admin dashboard showing statistics and attendance chart*

### Student Registration
![Registration](screenshots/registration.png)
*Student registration form with face image upload*

### Attendance Taking
![Take Attendance](screenshots/take_attendance.png)
*Real-time camera feed with face recognition*

### Attendance Records
![Records](screenshots/attendance_records.png)
*Filterable attendance records table*

### Student Management
![Students](screenshots/students.png)
*Student list with management options*

> **Note**: Screenshots should be added to a `screenshots/` directory in the project root.

---

## 🔌 API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | Home page | No |
| GET/POST | `/login` | Admin login | No |
| GET | `/logout` | Admin logout | No |
| GET | `/dashboard` | Admin dashboard | Yes |
| GET/POST | `/register` | Register student | Yes |
| GET | `/take_attendance` | Take attendance page | Yes |
| GET | `/video_feed` | Camera video stream | Yes |
| GET | `/students` | List all students | Yes |
| GET/POST | `/edit_student/<id>` | Edit student | Yes |
| POST | `/delete_student/<id>` | Delete student | Yes |
| GET | `/attendance_records` | View attendance records | Yes |
| GET | `/export_attendance` | Export CSV | Yes |

---

## 🗄 Database Schema

### Students Table
```sql
CREATE TABLE students (
    id INTEGER PRIMARY KEY,
    student_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    course TEXT,
    face_encoding BLOB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Attendance Table
```sql
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    status TEXT DEFAULT 'present',
    method TEXT DEFAULT 'face_recognition',
    confidence_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id),
    UNIQUE(student_id, date)
);
```

---

## 🚀 Future Scope

### Short-term Enhancements
- [ ] **Multi-camera Support**: Support for multiple camera inputs
- [ ] **Batch Registration**: CSV import for bulk student registration
- [ ] **Email Notifications**: Automated email alerts for attendance
- [ ] **Mobile Responsive**: Enhanced mobile interface optimization
- [ ] **Attendance Reports**: PDF report generation with charts

### Advanced Features
- [ ] **Machine Learning Improvements**: 
  - Fine-tuned face recognition models
  - Age and gender detection
  - Emotion recognition
- [ ] **Real-time Analytics**: 
  - Live attendance monitoring
  - Predictive analytics
  - Attendance trend analysis
- [ ] **Multi-user Support**: 
  - Role-based access control
  - Department/class management
  - Multiple admin accounts
- [ ] **Integration**: 
  - API endpoints for third-party integration
  - SMS notifications
  - Calendar integration
- [ ] **Security Enhancements**: 
  - Password hashing (bcrypt)
  - JWT authentication
  - Rate limiting
  - CSRF protection

### Scalability
- [ ] **Database Migration**: PostgreSQL/MySQL support
- [ ] **Cloud Deployment**: Docker containerization
- [ ] **Caching**: Redis for performance optimization
- [ ] **Load Balancing**: Multi-instance deployment

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide for Python code
- Write clear commit messages
- Add comments for complex logic
- Update documentation for new features

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👨‍💻 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com

---

## 🙏 Acknowledgments

- **face_recognition** library by Adam Geitgey
- **OpenCV** community for computer vision tools
- **Flask** framework developers
- **Bootstrap** team for UI components
- **Chart.js** for data visualization

---

## 📞 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Contact: your.email@example.com

---

<div align="center">

**Built with ❤️ using Python, Flask, and Computer Vision**

⭐ Star this repo if you find it helpful!

</div>
