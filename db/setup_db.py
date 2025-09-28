import os
from dotenv import load_dotenv
from db.db import TaskManager, TaskStatus

def setup_database():
    """Create the tasks table and populate it with sample data."""
    load_dotenv()

    tm = TaskManager()
    
    try:
        print("Creating tasks table...")
        tm.create_tasks_table()
        print("✓ Tasks table created successfully")
        
        # Sample task 1: A simple task
        task1_actions = {
            "steps": ["Research PostgreSQL documentation", "Set up local environment", "Test connection"],
            "estimated_time": "2 hours",
            "priority": "high"
        }
        
        task1_id = tm.create_task(
            description="Set up PostgreSQL database for task management system",
            actions=task1_actions,
            status=TaskStatus.STARTED,
            progress=0.7
        )
        print(f"✓ Created sample task 1 (ID: {task1_id})")
        
        # Sample task 2: A more complex task
        task2_actions = {
            "steps": [
                "Design API endpoints",
                "Implement CRUD operations",
                "Add authentication",
                "Write tests",
                "Deploy to production"
            ],
            "estimated_time": "1 week",
            "priority": "medium",
            "tags": ["backend", "api", "python"],
            "dependencies": ["database_setup"]
        }
        
        task2_id = tm.create_task(
            description="Build REST API for task management with n8n integration",
            actions=task2_actions,
            status=TaskStatus.NEW,
            progress=0.0
        )
        print(f"✓ Created sample task 2 (ID: {task2_id})")
        
        print("\nDatabase setup completed successfully!")
        print(f"Sample tasks created with IDs: {task1_id}, {task2_id}")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        raise
    finally:
        tm.close()

if __name__ == "__main__":
    setup_database()
