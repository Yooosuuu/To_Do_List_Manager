import sqlite3

# Classe pour gérer la base de données SQLite
class Database:
    def __init__(self, db_name="tasks.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()
        self.create_subtasks_table()
    
    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                priority TEXT CHECK(priority IN ('Faible', 'Normale', 'Haute')) DEFAULT 'Normale',
                status TEXT DEFAULT 'Non terminée',
                description TEXT,
                progress TEXT CHECK(progress IN ('Non commencé', 'En cours', 'Bientôt fini', 'Terminé')) DEFAULT 'Non commencé',
                duration TEXT CHECK(duration IN ('0-1h', '1-2h', '2-4h', '4-8h', '8-12h', '12-24h', '+24h')) DEFAULT '0-1h',
                deadline TEXT DEFAULT ''
            )
        """)
        self.conn.commit()
    
    def create_subtasks_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS subtasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                description TEXT NOT NULL,
                done INTEGER DEFAULT 0,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
            )
        """)
        self.conn.commit()
    
    def get_tasks(self):
        self.cursor.execute("""
            SELECT id, task, priority, status, description, progress, duration, deadline
            FROM tasks
        """)
        return self.cursor.fetchall()
    
    def get_task(self, task_id):
        self.cursor.execute("""
            SELECT id, task, priority, status, description, progress, duration, deadline
            FROM tasks
            WHERE id = ?
        """, (task_id,))
        return self.cursor.fetchone()
    
    def get_task_by_id(self, task_id):
        return self.get_task(task_id)
    
    def add_task(self, task_text, priority="Normale", description="", progress="Non commencé", duration="0-1h", deadline=""):
        self.cursor.execute("""
            INSERT INTO tasks (task, priority, description, progress, duration, deadline)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (task_text, priority, description, progress, duration, deadline))
        self.conn.commit()
        return self.cursor.lastrowid  # Retourne l'ID de la tâche ajoutée
    
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
    
    def update_task_progress(self, task_id, progress):
        self.cursor.execute("UPDATE tasks SET progress = ? WHERE id = ?", (progress, task_id))
        self.conn.commit()

    def update_task_details(self, task_id, task_text, priority, description, progress, duration, deadline):
        self.cursor.execute("""
            UPDATE tasks
            SET task = ?, priority = ?, description = ?, progress = ?, duration = ?, deadline = ?
            WHERE id = ?
        """, (task_text, priority, description, progress, duration, deadline, task_id))
        self.conn.commit()

    def clear_completed(self):
        self.cursor.execute("DELETE FROM tasks WHERE status = 'Terminée'")
        self.conn.commit()
        
    def sort_tasks(self):
        self.cursor.execute("""
            SELECT id, task, priority, status, description, progress, duration, deadline
            FROM tasks 
            ORDER BY 
                CASE priority
                    WHEN 'Haute' THEN 1
                    WHEN 'Normale' THEN 2
                    WHEN 'Faible' THEN 3
                END
        """)
        sorted_tasks = self.cursor.fetchall()
        self.cursor.execute("DELETE FROM tasks")
        for task in sorted_tasks:
            self.cursor.execute("""
                INSERT INTO tasks (id, task, priority, status, description, progress, duration, deadline)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, task)
        self.conn.commit()
        return sorted_tasks

    # Méthodes pour gérer les sous-tâches
    def get_subtasks(self, task_id):
        self.cursor.execute("""
            SELECT id, description, done FROM subtasks WHERE task_id = ?
        """, (task_id,))
        return self.cursor.fetchall()
    
    def add_subtask(self, task_id, description):
        self.cursor.execute("""
            INSERT INTO subtasks (task_id, description) VALUES (?, ?)
        """, (task_id, description))
        self.conn.commit()
    
    def update_subtask_status(self, subtask_id, done):
        self.cursor.execute("""
            UPDATE subtasks SET done = ? WHERE id = ?
        """, (1 if done else 0, subtask_id))
        self.conn.commit()

    def close(self):
        self.conn.close()
