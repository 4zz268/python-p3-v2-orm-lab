import sqlite3

CONN = sqlite3.connect('employees.db')
CURSOR = CONN.cursor()

class Employee:
    def __init__(self, name, salary, id=None):
        self.id = id
        self.name = name
        self.salary = salary

    @classmethod
    def create_table(cls):
        CURSOR.execute('''CREATE TABLE IF NOT EXISTS employees (id INTEGER PRIMARY KEY, name TEXT, salary REAL)''')
        CONN.commit()