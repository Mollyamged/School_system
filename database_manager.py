import sqlite3

class DatabaseManager:
    def __init__(self, db_name='school.db'):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()

    

    def close_connection(self):
        self.connection.close()