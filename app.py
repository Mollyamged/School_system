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

@app.route('/attendance_takinng')
def attendance_taking():
    return render_template('attendance_taking.html')