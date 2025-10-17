from flask import Flask, render_template, request, jsonify, session, url_for
from datetime import datetime, date, timedelta
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Configuration
DATA_FILE = 'attendance_data.json'

# Sample student data
students = [
    {"id": 1, "name": "Alice Johnson", "present": False},
    {"id": 2, "name": "Bob Smith", "present": False},
    {"id": 3, "name": "Carol Williams", "present": False},
    {"id": 4, "name": "David Brown", "present": False},
    {"id": 5, "name": "Eva Davis", "present": False},
    {"id": 6, "name": "Frank Miller", "present": False},
    {"id": 7, "name": "Grace Wilson", "present": False},
    {"id": 8, "name": "Henry Moore", "present": False}
]

def load_data():
    """Load attendance data from file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"attendance_records": [], "initialized_days": []}

def save_data(data):
    """Save attendance data to file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def is_day_initialized(check_date=None):
    """Check if day has already been initialized (meaning it's a school day)"""
    if check_date is None:
        check_date = date.today()
    
    data = load_data()
    date_str = check_date.isoformat()
    return date_str in data["initialized_days"]

def get_initialized_days_count():
    """Get total number of school days (initialized days)"""
    data = load_data()
    return len(data["initialized_days"])

def calculate_attendance_percentage(student_id):
    """Calculate attendance percentage for a student - ONLY COUNTING INITIALIZED DAYS"""
    data = load_data()
    
    total_school_days = len(data["initialized_days"])
    
    if total_school_days == 0:
        return 0
    
    # Count how many initialized days the student was present
    present_days = 0
    for initialized_day in data["initialized_days"]:
        # Check if we have attendance record for this student on this day
        day_present = False
        for record in data["attendance_records"]:
            record_date = record["date"].split('T')[0]  # Get just the date part
            
            if record_date == initialized_day:
                # Check if student was present in either session
                for student in record["students"]:
                    if student["id"] == student_id and student["present"]:
                        day_present = True
                        break
                if day_present:
                    break
        
        if day_present:
            present_days += 1
    
    return (present_days / total_school_days) * 100

def get_today_attendance_stats():
    """Get today's attendance statistics"""
    data = load_data()
    today_str = date.today().isoformat()
    
    present_count = 0
    absent_count = len(students)
    
    # Find today's attendance record
    for record in data["attendance_records"]:
        record_date = record["date"].split('T')[0]
        if record_date == today_str:
            present_count = sum(1 for student in record["students"] if student["present"])
            absent_count = len(students) - present_count
            break
    
    attendance_rate = (present_count / len(students)) * 100 if len(students) > 0 else 0
    
    return {
        "present": present_count,
        "absent": absent_count,
        "rate": round(attendance_rate, 1)
    }

@app.route('/')
def home():
    today_initialized = is_day_initialized()
    return render_template('home.html', today_initialized=today_initialized)

@app.route('/attendance/init')
def attendance_init():
    today_initialized = is_day_initialized()
    return render_template('attendance_init.html', today_initialized=today_initialized)

@app.route('/attendance/session')
def attendance_session():
    today_initialized = is_day_initialized()
    if not today_initialized:
        return render_template('error.html', 
                             message="Day not initialized. Please initialize the day first.",
                             redirect_url=url_for('attendance_init'))
    return render_template('attendance_session.html')

@app.route('/attendance/taking')
def attendance_taking():
    today_initialized = is_day_initialized()
    if not today_initialized:
        return render_template('error.html', 
                             message="Day not initialized. Please initialize the day first.",
                             redirect_url=url_for('attendance_init'))
    
    session_type = request.args.get('session', 'before-break')
    
    # Load today's attendance data if exists
    today_stats = get_today_attendance_stats()
    
    # Load student data with attendance percentages
    students_with_percentage = []
    for student in students:
        percentage = calculate_attendance_percentage(student["id"])
        students_with_percentage.append({
            **student,
            "attendance_percentage": round(percentage, 1)
        })
    
    return render_template('attendance_taking.html', 
                         session_type=session_type, 
                         students=students_with_percentage,
                         today_stats=today_stats)

@app.route('/api/initialize_day', methods=['POST'])
def initialize_day():
    today = date.today()
    
    # Check if day already initialized
    if is_day_initialized(today):
        return jsonify({
            'status': 'error', 
            'message': 'Day has already been initialized.'
        }), 400
    
    # Initialize the day (mark it as a school day)
    data = load_data()
    date_str = today.isoformat()
    data["initialized_days"].append(date_str)
    save_data(data)
    
    return jsonify({
        'status': 'success', 
        'message': 'Day initialized successfully! Today is now marked as a school day.'
    })

@app.route('/api/submit_attendance', methods=['POST'])
def submit_attendance():
    data = request.json
    today = date.today()
    
    # Verify day is initialized
    if not is_day_initialized(today):
        return jsonify({
            'status': 'error', 
            'message': 'Day not initialized. Please initialize the day first.'
        }), 400
    
    # Save or update attendance record
    attendance_data = load_data()
    
    # Remove existing record for today if exists
    today_str = today.isoformat()
    attendance_data["attendance_records"] = [
        record for record in attendance_data["attendance_records"] 
        if not record["date"].startswith(today_str)
    ]
    
    # Add new record
    attendance_data["attendance_records"].append({
        "date": datetime.now().isoformat(),
        "session": data["session"],
        "students": data["students"]
    })
    
    save_data(attendance_data)
    
    return jsonify({
        'status': 'success', 
        'message': 'Attendance submitted successfully!'
    })

@app.route('/api/attendance_stats')
def attendance_stats():
    """API endpoint to get attendance statistics"""
    stats = {}
    for student in students:
        percentage = calculate_attendance_percentage(student["id"])
        stats[student["id"]] = {
            "name": student["name"],
            "attendance_percentage": round(percentage, 1)
        }
    
    return jsonify(stats)

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard to view statistics"""
    total_school_days = get_initialized_days_count()
    
    student_stats = []
    for student in students:
        percentage = calculate_attendance_percentage(student["id"])
        student_stats.append({
            "id": student["id"],
            "name": student["name"],
            "attendance_percentage": round(percentage, 1)
        })
    
    return render_template('admin_dashboard.html', 
                         student_stats=student_stats,
                         total_school_days=total_school_days)

if __name__ == '__main__':
    app.run(debug=True)