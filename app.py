from datetime import date
from flask import Flask, render_template, request

from database_manager import DatabaseManager

app = Flask(__name__)

database_manager = DatabaseManager()


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/attendance_init', methods=["GET", "POST"])
def attendance_init():
    if request.method == "POST":
        database_manager.init_day(date.today().strftime("%d-%m-%Y"))
    
    is_initialized = database_manager.is_day_initialized(date.today().strftime("%d-%m-%Y"))
    return render_template('attendance_init.html', today_initialized=is_initialized)

@app.route('/attendance_session')
def attendance_session():
    return render_template('attendance_session.html')


@app.route('/attendance_classes')
def attendance_classes():

    session = request.args.get('session')

    return render_template(
        'attendance_classes.html',
        g1classes=database_manager.get_classes(1),
        g2classes=database_manager.get_classes(2),
        g3classes=database_manager.get_classes(3),
        session = session,
    )

@app.route('/attendance_taking', methods=["GET", "POST"])
def attendance_taking():
    session = request.args.get('session')

    if request.method == "POST":
        attended_students = list(request.form.keys())
        database_manager.update_attendance(date.today().strftime("%d-%m-%Y"), attended_students, session=="before-break")

    students = database_manager.get_students_by_class(request.args.get('class'))
    return render_template('attendance_taking.html', session=session, students=students)