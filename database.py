import sqlite3
import threading


class DatabaseHandler:
    def __init__(self, db_name="tasks.db"):
        self.lock = threading.Lock()
        self.connection = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        with self.lock:
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    min_time INTEGER,
                    max_time INTEGER,
                    elapsed_time INTEGER DEFAULT 0,
                    checkmark INTEGER DEFAULT 0
                )
            """
            )
            self.connection.commit()

    def add_task(self, name, min_time, max_time):
        with self.lock:
            self.cursor.execute(
                """
                INSERT INTO tasks (name, min_time, max_time) VALUES (?, ?, ?)
            """,
                (name, min_time, max_time),
            )
            self.connection.commit()

    def remove_task(self, task_id):
        with self.lock:
            self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            self.connection.commit()

    def update_task(self, task_id, elapsed_time, checkmark):
        with self.lock:
            self.cursor.execute(
                """
                UPDATE tasks
                SET elapsed_time = ?, checkmark = ?
                WHERE id = ?
            """,
                (elapsed_time, checkmark, task_id),
            )
            self.connection.commit()

    def get_tasks(self):
        with self.lock:
            self.cursor.execute("SELECT * FROM tasks")
            return self.cursor.fetchall()

    def close(self):
        self.connection.close()
