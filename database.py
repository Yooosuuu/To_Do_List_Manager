import sqlite3

class Database:
    def __init__(self, db_name="tasks.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()
    
    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                priority TEXT CHECK(priority IN ('Faible', 'Normale', 'Haute')) DEFAULT 'Normale',
                status TEXT DEFAULT 'Non terminée'
            )
        """)
        self.conn.commit()
    
    def get_tasks(self):
        self.cursor.execute("SELECT id, task, priority, status FROM tasks")
        return self.cursor.fetchall()
    
    def add_task(self, task_text, priority="Normale"):
        self.cursor.execute("INSERT INTO tasks (task, priority) VALUES (?, ?)", (task_text, priority))
        self.conn.commit()
    
    def delete_task(self, task_id):
        self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()
    
    def update_task_text(self, task_id, new_text):
        self.cursor.execute("UPDATE tasks SET task = ? WHERE id = ?", (new_text, task_id))
        self.conn.commit()

    def update_priority(self, task_id, priority):
        self.cursor.execute("UPDATE tasks SET priority = ? WHERE id = ?", (priority, task_id))
        self.conn.commit()

    def update_task_status(self, task_id, status):
        self.cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
        self.conn.commit()

    def clear_completed(self):
        self.cursor.execute("DELETE FROM tasks WHERE status = 'Terminée'")
        self.conn.commit()
    
    def close(self):
        self.conn.close()
