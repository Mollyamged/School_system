import sqlite3

def create_database():
    conn = sqlite3.connect('school.db')
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")

    # Create classes first (referenced table)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS classes (
            grade INTEGER NOT NULL,
            class TEXT NOT NULL,
            PRIMARY KEY (grade, class)
        )
    ''')

    # Create students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            ssn TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            num_absences INTEGER DEFAULT 0,
            grade INTEGER NOT NULL,
            class TEXT NOT NULL,
            FOREIGN KEY (grade, class) REFERENCES classes (grade, class)
        )
    ''')

    # Create courses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            cid INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT NOT NULL,
            grade INTEGER NOT NULL,
            term INTEGER CHECK(term IN (1,2))
        )
    ''')

    # Create grades table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grades (
            student_ssn TEXT,
            course_id INTEGER,
            scores INTEGER,
            PRIMARY KEY (student_ssn, course_id),
            FOREIGN KEY (student_ssn) REFERENCES students (ssn),
            FOREIGN KEY (course_id) REFERENCES courses (cid)
        )
    ''')

    # Create attendance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            student_ssn TEXT,
            date TEXT,
            before_break_attendance BOOLEAN DEFAULT NULL,
            after_break_attendance BOOLEAN DEFAULT NULL,
            PRIMARY KEY (student_ssn, date),
            FOREIGN KEY (student_ssn) REFERENCES students (ssn)
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
