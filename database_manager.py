import sqlite3

class DatabaseManager:
    def __init__(self, db_name='school.db'):
        self.db_name = db_name


    def is_day_initialized(self, date: str) -> bool:
        _, cursor = self._get_conn_and_cursor()
        cursor.execute('SELECT * FROM attendance WHERE date = ? LIMIT 1', (date,))
        return cursor.fetchone() is not None

    def init_day(self, date: str) -> None:
        connection, cursor = self._get_conn_and_cursor()
        cursor.execute('SELECT ssn FROM students')
        rows = cursor.fetchall()
        for row in rows:
            id = row[0]
            cursor.execute("INSERT INTO attendance (student_ssn, date) VALUES (?, ?)", (id, date))
            connection.commit()

    def update_attendance(self, date: str, ssns: list[str], before_break: bool):
        connection, cursor = self._get_conn_and_cursor()

        if not ssns:
            return  # Nothing to update, avoid SQL error from empty IN ()

        attendance_column_name = (
            'before_break_attendance' if before_break else 'after_break_attendance'
        )

        placeholders = ','.join('?' * len(ssns))
        sql = f'''
            UPDATE attendance
            SET {attendance_column_name} = 1
            WHERE date = ?
            AND student_ssn IN ({placeholders})
        '''

        # Combine parameters into one flat tuple
        cursor.execute(sql, (date, *ssns))
        connection.commit()

    def get_classes(self, grade: int):
        _, cursor = self._get_conn_and_cursor()
        cursor.execute('SELECT class, grade FROM classes WHERE grade = ?', (grade,))
        return cursor.fetchall()        

    def get_students_by_class(self, cls: str):
        _, cursor = self._get_conn_and_cursor()

        cursor.execute('SELECT ssn, name FROM students WHERE class = ?', (cls,))
        return cursor.fetchall()

    def _get_conn_and_cursor(self) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        return connection, cursor

    def close_connection(self):
        self.connection.close()