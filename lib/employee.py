from lib import CONN, CURSOR

class Employee:
    all = {}

    def __init__(self, name, job_title, department_id, id=None):
        self.id = id
        self.name = name
        self.job_title = job_title
        self.department_id = department_id

    def __repr__(self):
        return f"<Employee id={self.id} name={self.name} job_title={self.job_title} department_id={self.department_id}>"

    @classmethod
    def create_table(cls):
        sql = '''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            job_title TEXT,
            department_id INTEGER,
            FOREIGN KEY (department_id) REFERENCES departments(id)
        )'''
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        sql = "DROP TABLE IF EXISTS employees;"
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        if self.id is None:
            sql = '''
            INSERT INTO employees (name, job_title, department_id)
            VALUES (?, ?, ?)
            '''
            CURSOR.execute(sql, (self.name, self.job_title, self.department_id))
            CONN.commit()
            self.id = CURSOR.lastrowid
            Employee.all[self.id] = self
        else:
            self.update()
        return self

    @classmethod
    def create(cls, name, job_title, department_id):
        employee = cls(name, job_title, department_id)
        employee.save()
        return employee

    @classmethod
    def instance_from_db(cls, row):
        if row is None:
            return None
        employee_id = row[0]
        if employee_id in cls.all:
            instance = cls.all[employee_id]
            instance.name = row[1]
            instance.job_title = row[2]
            instance.department_id = row[3]
            return instance
        else:
            instance = cls(row[1], row[2], row[3], id=employee_id)
            cls.all[employee_id] = instance
            return instance

    @classmethod
    def find_by_id(cls, id):
        sql = "SELECT * FROM employees WHERE id = ?;"
        CURSOR.execute(sql, (id,))
        row = CURSOR.fetchone()
        return cls.instance_from_db(row)

    @classmethod
    def find_by_name(cls, name):
        sql = "SELECT * FROM employees WHERE name = ?;"
        CURSOR.execute(sql, (name,))
        row = CURSOR.fetchone()
        return cls.instance_from_db(row)

    def update(self):
        if self.id is None:
            raise ValueError("Cannot update employee without id.")
        sql = '''
        UPDATE employees
        SET name = ?, job_title = ?, department_id = ?
        WHERE id = ?
        '''
        CURSOR.execute(sql, (self.name, self.job_title, self.department_id, self.id))
        CONN.commit()
        Employee.all[self.id] = self

    def delete(self):
        if self.id is None:
            return
        sql = "DELETE FROM employees WHERE id = ?;"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        if self.id in Employee.all:
            del Employee.all[self.id]
        self.id = None

    @classmethod
    def get_all(cls):
        sql = "SELECT * FROM employees;"
        CURSOR.execute(sql)
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]

    def reviews(self):
        from lib.review import Review
        sql = "SELECT * FROM reviews WHERE employee_id = ?;"
        CURSOR.execute(sql, (self.id,))
        rows = CURSOR.fetchall()
        return [Review.instance_from_db(row) for row in rows]

    # --- Properties ---
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str) or len(value.strip()) == 0:
            raise ValueError("Name must be a non-empty string.")
        self._name = value.strip()

    @property
    def job_title(self):
        return self._job_title

    @job_title.setter
    def job_title(self, value):
        if not isinstance(value, str) or len(value.strip()) == 0:
            raise ValueError("Job title must be a non-empty string.")
        self._job_title = value.strip()

    @property
    def department_id(self):
        return self._department_id

    @department_id.setter
    def department_id(self, value):
        from lib.department import Department
        if not isinstance(value, int):
            raise ValueError("Department ID must be an integer.")
        if Department.find_by_id(value) is None:
            raise ValueError(f"No department with id {value} exists.")
        self._department_id = value