import sqlite3

def create_database():
    # Connect to SQLite database (creates a new database if it doesn't exist)
    conn = sqlite3.connect('school.db')
    cursor = conn.cursor()

    # Create students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            ssn TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            grade INTEGER NOT NULL,
            class CHAR NOT NULL
        )
    ''')

    # Create courses table with a foreign key referencing students
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            student_ssn TEXT,
            date TEXT,
            before_break_attendance BOOLEAN DEFAULT NULL,
            after_break_attendance BOOLEAN DEFAULT NULL,
            FOREIGN KEY (student_ssn) REFERENCES students (ssn),
            PRIMARY KEY (student_ssn, date)
        )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()