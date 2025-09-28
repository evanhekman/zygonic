import os
import psycopg2
import psycopg2.extras
from enum import Enum
from typing import Dict, List, Optional, Union
from datetime import datetime
import json

class TaskStatus(Enum):
    NEW = "NEW"
    STARTED = "STARTED"
    COMPLETED = "COMPLETED"

class DatabaseConnection:
    def __init__(self):
        self.conn = None
        self.connect()
    
    def connect(self):
        """Connect to PostgreSQL database using environment variables."""
        try:
            self.conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'taskmanager'),
                user=os.getenv('DB_USER', 'dev'),
                password=os.getenv('DB_PASSWORD', 'devpass'),
                port=os.getenv('DB_PORT', '5432')
            )
            self.conn.autocommit = True
        except psycopg2.Error as e:
            raise Exception(f"Failed to connect to database: {e}")
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

class TaskManager:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def create_tasks_table(self):
        """Create the tasks table with all required fields."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            description TEXT NOT NULL,
            actions JSONB DEFAULT '{}',
            status VARCHAR(20) DEFAULT 'NEW' CHECK (status IN ('NEW', 'STARTED', 'COMPLETED')),
            progress FLOAT DEFAULT 0.0 CHECK (progress >= 0.0 AND progress <= 1.0),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
        CREATE INDEX IF NOT EXISTS idx_tasks_progress ON tasks(progress);
        CREATE INDEX IF NOT EXISTS idx_tasks_actions ON tasks USING GIN (actions);
        """
        
        try:
            with self.db.conn.cursor() as cursor:
                cursor.execute(create_table_query)
        except psycopg2.Error as e:
            raise Exception(f"Failed to create tasks table: {e}")
    
    def create_task(self, description: str, actions: Dict = None, 
                   status: TaskStatus = TaskStatus.NEW, progress: float = 0.0) -> int:
        """Create a new task and return its id."""
        if actions is None:
            actions = {}
        
        if not 0.0 <= progress <= 1.0:
            raise ValueError("Progress must be between 0.0 and 1.0")
        
        insert_query = """
        INSERT INTO tasks (description, actions, status, progress)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
        """
        
        try:
            with self.db.conn.cursor() as cursor:
                cursor.execute(insert_query, (
                    description,
                    json.dumps(actions),
                    status.value,
                    progress
                ))
                id = cursor.fetchone()[0]
                return id
        except psycopg2.Error as e:
            raise Exception(f"Failed to create task: {e}")
    
    def get_task(self, id: int) -> Optional[Dict]:
        """Retrieve a task by its ID."""
        select_query = """
        SELECT id, description, actions, status, progress, 
               created_at, updated_at
        FROM tasks WHERE id = %s;
        """
        
        try:
            with self.db.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(select_query, (id,))
                result = cursor.fetchone()
                if result:
                    return dict(result)
                return None
        except psycopg2.Error as e:
            raise Exception(f"Failed to retrieve task {id}: {e}")
    
    def get_all_tasks(self) -> List[Dict]:
        """Retrieve all tasks."""
        select_query = """
        SELECT id, description, actions, status, progress,
               created_at, updated_at
        FROM tasks ORDER BY created_at DESC;
        """
        
        try:
            with self.db.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(select_query)
                results = cursor.fetchall()
                return [dict(row) for row in results]
        except psycopg2.Error as e:
            raise Exception(f"Failed to retrieve tasks: {e}")
    
    def update_task(self, id: int, **kwargs) -> bool:
        """Update a task with given fields. Returns True if task was found and updated."""
        allowed_fields = ['description', 'actions', 'status', 'progress']
        updates = []
        values = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                if field == 'status' and isinstance(value, TaskStatus):
                    value = value.value
                elif field == 'actions' and isinstance(value, dict):
                    value = json.dumps(value)
                elif field == 'progress' and not 0.0 <= value <= 1.0:
                    raise ValueError("Progress must be between 0.0 and 1.0")
                
                updates.append(f"{field} = %s")
                values.append(value)
        
        if not updates:
            raise ValueError("No valid fields provided for update")
        
        # Add updated_at
        updates.append("updated_at = CURRENT_TIMESTAMP")
        
        update_query = f"""
        UPDATE tasks SET {', '.join(updates)}
        WHERE id = %s;
        """
        values.append(id)
        
        try:
            with self.db.conn.cursor() as cursor:
                cursor.execute(update_query, values)
                return cursor.rowcount > 0
        except psycopg2.Error as e:
            raise Exception(f"Failed to update task {id}: {e}")
    
    def delete_task(self, id: int) -> bool:
        """Delete a task by ID. Returns True if task was found and deleted."""
        delete_query = "DELETE FROM tasks WHERE id = %s;"
        
        try:
            with self.db.conn.cursor() as cursor:
                cursor.execute(delete_query, (id,))
                return cursor.rowcount > 0
        except psycopg2.Error as e:
            raise Exception(f"Failed to delete task {id}: {e}")
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Dict]:
        """Get all tasks with a specific status."""
        select_query = """
        SELECT id, description, actions, status, progress,
               created_at, updated_at
        FROM tasks WHERE status = %s ORDER BY created_at DESC;
        """
        
        try:
            with self.db.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(select_query, (status.value,))
                results = cursor.fetchall()
                return [dict(row) for row in results]
        except psycopg2.Error as e:
            raise Exception(f"Failed to retrieve tasks by status: {e}")
    
    def drop_tasks_table(self):
        """Drop the tasks table. Use with caution!"""
        drop_query = "DROP TABLE IF EXISTS tasks CASCADE;"
        
        try:
            with self.db.conn.cursor() as cursor:
                cursor.execute(drop_query)
        except psycopg2.Error as e:
            raise Exception(f"Failed to drop tasks table: {e}")
    
    def close(self):
        """Close database connection."""
        self.db.close()

# Convenience functions for easy importing
def get_task_manager():
    """Factory function to get a TaskManager instance."""
    return TaskManager()
