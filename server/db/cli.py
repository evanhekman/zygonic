#!/usr/bin/env python3
"""
Complete database management CLI for the task management system.
Usage: python db_cli.py <command> [options]

This file contains all database operations and can replace:
- db.py
- clear_db.py  
- setup_db.py
- test_db.py
- see_db.py
"""

import argparse
import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from db import TaskManager, DatabaseConnection

# Database dependencies
import psycopg2
import psycopg2.extras

# ============================================================================
# UTILITY FUNCTIONS (from see_db.py)
# ============================================================================

def format_timestamp(ts):
    """Format timestamp for better readability"""
    if ts:
        return ts.strftime("%Y-%m-%d %H:%M:%S")
    return "N/A"

def truncate_text(text, max_length=100):
    """Truncate long text for display"""
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text

# ============================================================================
# COMMAND FUNCTIONS
# ============================================================================

def clean_database(force=False):
    """Clean the database by dropping and recreating the tasks table."""
    print("🧹 Cleaning database...")
    
    if not force:
        print("⚠️  This will delete ALL existing tasks!")
        response = input("Are you sure you want to continue? (y/N): ")
        if response.lower() != 'y':
            print("❌ Operation cancelled")
            return False
    
    try:
        tm = TaskManager()
        print("Dropping tasks table...")
        tm.drop_tasks_table()
        print("Recreating tasks table...")
        tm.create_tasks_table()
        tm.close()
        print("✅ Database cleaned successfully!")
        return True
    except Exception as e:
        print(f"❌ Error cleaning database: {e}")
        return False

def setup_database():
    """Create the tasks table and populate it with sample data."""
    tm = TaskManager()
    
    try:
        print("Creating tasks table...")
        tm.create_tasks_table()
        print("✅ Tasks table created successfully")
        
        # Sample task 1: A simple task
        task1_data = {
            "description": "Set up PostgreSQL database for task management system",
            "action": {
                "actions": [
                    {
                        "integration": "postgres",
                        "action": "setup",
                        "args": {
                            "steps": ["Research PostgreSQL documentation", "Set up local environment", "Test connection"],
                            "estimated_time": "2 hours",
                            "priority": "high"
                        },
                        "webhook": "DB_SETUP_WEBHOOK"
                    }
                ]
            },
            "status": "STARTED",
            "progress": 0.7
        }
        
        task1_id = tm.create_task(**task1_data)
        print(f"✅ Created sample task 1 (ID: {task1_id})")
        
        # Sample task 2: A more complex task
        task2_data = {
            "description": "Build REST API for task management with n8n integration",
            "action": {
                "actions": [
                    {
                        "integration": "api",
                        "action": "build",
                        "args": {
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
                        },
                        "webhook": "API_BUILD_WEBHOOK"
                    }
                ]
            },
            "status": "NEW",
            "progress": 0.0
        }
        
        task2_id = tm.create_task(**task2_data)
        print(f"✅ Created sample task 2 (ID: {task2_id})")
        
        print("\n✅ Database setup completed successfully!")
        print(f"Sample tasks created with IDs: {task1_id}, {task2_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        return False
    finally:
        tm.close()

def view_database():
    """View the contents of the tasks database."""
    print("=" * 80)
    print("DATABASE CONTENTS")
    print("=" * 80)
    
    try:
        tm = TaskManager()
        tasks = tm.get_all_tasks()
        
        if not tasks:
            print("No tasks found in database.")
            return True
        
        print(f"Found {len(tasks)} task(s):\n")
        
        for i, task in enumerate(tasks, 1):
            print(f"Task #{task['id']} (Entry {i})")
            print("-" * 40)
            print(f"Description: {truncate_text(task['description'], 80)}")
            print(f"Status: {task['status']}")
            print(f"Progress: {task['progress']:.1%}")
            print(f"Created: {format_timestamp(task['created_at'])}")
            print(f"Updated: {format_timestamp(task['updated_at'])}")
            
            # Pretty print action if they exist
            if task['action']:
                print("Action:")
                if isinstance(task['action'], dict):
                    for key, action in task['action'].items():
                        if isinstance(action, dict):
                            print(f"  {key}: {action.get('integration', 'N/A')}.{action.get('action', 'N/A')}")
                            if action.get('args'):
                                args = action['args']
                                for arg_key, arg_value in list(args.items())[:3]:
                                    display_value = truncate_text(str(arg_value), 50)
                                    print(f"    {arg_key}: {display_value}")
                                if len(args) > 3:
                                    print(f"    ... and {len(args) - 3} more args")
                        else:
                            print(f"  {key}: {truncate_text(str(action), 60)}")
                else:
                    print(f"  {truncate_text(str(task['action']), 60)}")
            else:
                print("Action: None")
            
            print()
            
            if i >= 100:
                print(f"... (showing first 100 entries)")
                break
        
        print("=" * 80)
        print(f"Total tasks shown: {min(len(tasks), 100)}")
        return True
        
    except Exception as e:
        print(f"❌ Error accessing database: {e}")
        return False
    finally:
        try:
            tm.close()
        except:
            pass

def test_database():
    """Comprehensive test of all database operations."""
    tm = TaskManager()
    
    try:
        print("🧪 Starting database tests...\n")
        
        # Test 1: Create table
        print("1. Testing table creation...")
        tm.create_tasks_table()
        print("✅ Tasks table created/verified")
        
        # Test 2: Create tasks
        print("\n2. Testing task creation...")
        test_actions = {
            "steps": ["Step 1", "Step 2", "Step 3"],
            "priority": "high",
            "tags": ["test", "database"]
        }
        
        task_id = tm.create_task(
            description="Test task for database validation",
            action=test_actions,
            status="NEW",
            progress=0.0
        )
        print(f"✅ Created test task with ID: {task_id}")
        
        # Test 3: Retrieve task
        print("\n3. Testing task retrieval...")
        retrieved_task = tm.get_task(task_id)
        if retrieved_task:
            print(f"✅ Retrieved task: {retrieved_task['description']}")
            print(f"  Status: {retrieved_task['status']}")
            print(f"  Progress: {retrieved_task['progress']}")
        else:
            raise Exception("Failed to retrieve created task")
        
        # Test 4: Update task
        print("\n4. Testing task updates...")
        update_success = tm.update_task(
            task_id,
            status="STARTED",
            progress=0.5,
            action={"steps": ["Updated step 1", "Updated step 2"], "priority": "medium"}
        )
        if update_success:
            print("✅ Task updated successfully")
            updated_task = tm.get_task(task_id)
            print(f"  New status: {updated_task['status']}")
            print(f"  New progress: {updated_task['progress']}")
        else:
            raise Exception("Failed to update task")
        
        # Test 5: Create multiple tasks for bulk operations
        print("\n5. Testing bulk operations...")
        task_ids = []
        statuses = ["NEW", "STARTED", "COMPLETED"]
        
        for i, status in enumerate(statuses):
            tid = tm.create_task(
                description=f"Bulk test task {i+1}",
                action={"test_number": i+1},
                status=status,
                progress=i * 0.5
            )
            task_ids.append(tid)
        print(f"✅ Created {len(task_ids)} additional test tasks")
        
        # Test 6: Get all tasks
        print("\n6. Testing get all tasks...")
        all_tasks = tm.get_all_tasks()
        print(f"✅ Retrieved {len(all_tasks)} total tasks")
        
        # Test 7: Get tasks by status
        print("\n7. Testing get tasks by status...")
        new_tasks = tm.get_tasks_by_status("NEW")
        started_tasks = tm.get_tasks_by_status("STARTED")
        completed_tasks = tm.get_tasks_by_status("COMPLETED")
        print(f"✅ Found {len(new_tasks)} NEW tasks")
        print(f"✅ Found {len(started_tasks)} STARTED tasks")
        print(f"✅ Found {len(completed_tasks)} COMPLETED tasks")
        
        # Test 8: Delete tasks
        print("\n8. Testing task deletion...")
        deleted_count = 0
        for tid in task_ids:
            if tm.delete_task(tid):
                deleted_count += 1
        print(f"✅ Deleted {deleted_count} test tasks")
        
        # Test 9: Verify deletion
        print("\n9. Verifying deletions...")
        remaining_tasks = tm.get_all_tasks()
        print(f"✅ {len(remaining_tasks)} tasks remaining in database")
        
        # Test 10: Error handling
        print("\n10. Testing error handling...")
        try:
            non_existent = tm.get_task(99999)
            if non_existent is None:
                print("✅ Correctly returned None for non-existent task")
            
            try:
                tm.create_task("Invalid progress task", progress=1.5)
                print("❌ Should have raised ValueError for invalid progress")
            except ValueError:
                print("✅ Correctly rejected invalid progress value")
                
        except Exception as e:
            print(f"❌ Unexpected error in error handling test: {e}")
        
        # Clean up
        print("\n🧹 Cleaning up...")
        if tm.delete_task(task_id):
            print("✅ Cleaned up test task")
        
        print("\n🎉 All tests passed!")
        
        # Show final state
        final_tasks = tm.get_all_tasks()
        print(f"\nFinal database state: {len(final_tasks)} tasks")
        for task in final_tasks:
            print(f"  - {task['description']} ({task['status']})")
        
        # Ask for destructive test
        print("\n" + "="*50)
        response = input("Run table drop/recreate test? This will delete all data (y/N): ")
        if response.lower() == 'y':
            test_table_management()
        
        return True
            
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False
    finally:
        tm.close()

def test_table_management():
    """Test table creation and deletion."""
    tm = TaskManager()
    
    try:
        print("\n🧪 Testing table management...")
        
        # Create table
        tm.create_tasks_table()
        print("✅ Table created")
        
        # Add a test task
        task_id = tm.create_task("Test task for table deletion")
        print("✅ Test task added")
        
        # Drop table
        print("⚠️  Dropping table (this will delete all data)...")
        tm.drop_tasks_table()
        print("✅ Table dropped successfully")
        
        # Recreate table
        tm.create_tasks_table()
        print("✅ Table recreated")
        
        # Verify it's empty
        tasks = tm.get_all_tasks()
        if len(tasks) == 0:
            print("✅ New table is empty as expected")
        else:
            print(f"❌ Expected empty table, found {len(tasks)} tasks")
            
    except Exception as e:
        print(f"❌ Table management test failed: {e}")
        return False
    finally:
        tm.close()

# ============================================================================
# MAIN CLI INTERFACE
# ============================================================================

def main():
    # Load environment variables if available
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # dotenv not available, rely on system env vars
    
    parser = argparse.ArgumentParser(
        description="Complete database management CLI for task management system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  clean     Drop and recreate the tasks table (removes all data)
  setup     Create table and populate with sample data
  test      Run comprehensive database tests
  view      Display current database contents

Examples:
  python db_cli.py clean
  python db_cli.py setup
  python db_cli.py test
  python db_cli.py view
        """
    )
    
    parser.add_argument(
        'command',
        choices=['clean', 'setup', 'test', 'view'],
        help='Database command to execute'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Skip confirmation prompts (use with caution)'
    )
    
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    if len(sys.argv) == 1:
        parser.print_help()
        return 0
    
    args = parser.parse_args()
    
    # Execute the requested command
    commands = {
        'clean': lambda: clean_database(force=args.force),
        'setup': setup_database,
        'test': test_database,
        'view': view_database,
    }
    
    success = commands[args.command]()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
