// Global variables
let currentSession = '';
let dayInitialized = false;

// Display current date
function displayCurrentDate() {
    const now = new Date();
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    const dateString = now.toLocaleDateString('en-US', options);
    
    const currentDateElement = document.getElementById('current-date');
    const attendanceDateElement = document.getElementById('attendance-date');
    
    if (currentDateElement) {
        currentDateElement.textContent = dateString;
    }
    if (attendanceDateElement) {
        attendanceDateElement.textContent = dateString;
    }
}

// Initialize the day for attendance
async function initializeDay() {
    try {
        const response = await fetch('/api/initialize_day', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            dayInitialized = true;
            const proceedBtn = document.getElementById('proceed-btn');
            if (proceedBtn) {
                proceedBtn.disabled = false;
                proceedBtn.textContent = 'Proceed to Attendance';
                proceedBtn.onclick = function() {
                    window.location.href = '/attendance/session';
                };
            }
            
            // Update the status display
            const dayStatus = document.querySelector('.day-status');
            if (dayStatus) {
                dayStatus.innerHTML = `
                    <div class="status-indicator status-present">✅ Today is a School Day</div>
                    <p class="info-message">
                        <strong>Today has been initialized as a school day.</strong><br>
                        Attendance will be counted in student percentages.
                    </p>
                `;
            }
            
            alert(data.message);
        } else {
            alert('Error: ' + data.message);
        }
    } catch (error) {
        console.error('Error initializing day:', error);
        alert('Error initializing day. Please try again.');
    }
}

// Toggle student attendance status
function toggleAttendance(studentId, isPresent) {
    const studentItem = document.querySelector(`[data-student-id="${studentId}"]`);
    const statusIndicator = studentItem.querySelector('.status-indicator');
    
    if (isPresent) {
        statusIndicator.textContent = 'Present';
        statusIndicator.className = 'status-indicator status-present';
    } else {
        statusIndicator.textContent = 'Absent';
        statusIndicator.className = 'status-indicator status-absent';
    }
    
    updateAttendanceSummary();
}

// Update attendance summary
function updateAttendanceSummary() {
    const studentItems = document.querySelectorAll('.student-item');
    const total = studentItems.length;
    let present = 0;
    
    studentItems.forEach(item => {
        const checkbox = item.querySelector('input[type="checkbox"]');
        if (checkbox && checkbox.checked) {
            present++;
        }
    });
    
    const absent = total - present;
    const attendanceRate = total > 0 ? (present / total) * 100 : 0;
    
    const presentCountElement = document.getElementById('present-count');
    const absentCountElement = document.getElementById('absent-count');
    const attendanceRateElement = document.getElementById('attendance-rate');
    
    if (presentCountElement) presentCountElement.textContent = present;
    if (absentCountElement) absentCountElement.textContent = absent;
    if (attendanceRateElement) attendanceRateElement.textContent = attendanceRate.toFixed(1) + '%';
}

// Submit attendance
async function submitAttendance() {
    const attendanceData = {
        session: currentSession || new URLSearchParams(window.location.search).get('session'),
        date: new Date().toISOString().split('T')[0],
        students: []
    };
    
    document.querySelectorAll('.student-item').forEach(item => {
        const studentId = item.getAttribute('data-student-id');
        const checkbox = item.querySelector('input[type="checkbox"]');
        const studentName = item.querySelector('.student-name').textContent;
        
        attendanceData.students.push({
            id: parseInt(studentId),
            name: studentName,
            present: checkbox ? checkbox.checked : false
        });
    });
    
    try {
        const response = await fetch('/api/submit_attendance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(attendanceData)
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            const presentCount = attendanceData.students.filter(s => s.present).length;
            const absentCount = attendanceData.students.length - presentCount;
            const sessionName = attendanceData.session === 'before-break' ? 'Before Break' : 'After Break';
            
            alert(`Attendance submitted successfully!\n\nPresent: ${presentCount}\nAbsent: ${absentCount}\nSession: ${sessionName}`);
            
            // Return to home page
            window.location.href = '/';
        } else {
            alert('Error: ' + data.message);
        }
    } catch (error) {
        console.error('Error submitting attendance:', error);
        alert('Error submitting attendance. Please try again.');
    }
}

// Load school days count
async function loadSchoolDaysCount() {
    try {
        const response = await fetch('/api/attendance_stats');
        const data = await response.json();
        
        // Count unique initialized days from the server data
        // In a real implementation, you'd have an API endpoint for this
        const schoolDaysElement = document.getElementById('school-days-count');
        if (schoolDaysElement) {
            schoolDaysElement.textContent = 'Calculated from initialized days only';
        }
    } catch (error) {
        console.error('Error loading school days count:', error);
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    displayCurrentDate();
    
    // Initialize attendance summary if on attendance taking page
    if (document.getElementById('student-list')) {
        updateAttendanceSummary();
    }
    
    // Load school days count if on init page
    if (document.getElementById('school-days-count')) {
        loadSchoolDaysCount();
    }
});