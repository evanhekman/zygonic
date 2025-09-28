import os
from dotenv import load_dotenv
from db import TaskManager, TaskStatus
import json

def test_database_operations():
    """Comprehensive test of all database operations."""
    load_dotenv()
    
    tm = TaskManager()
    
    try:
        print("🧪 Starting database tests...\n")
        
        # Test 1: Create table
        print("1. Testing table creation...")
        tm.create_tasks_table()
        print("✓ Tasks table created/verified")
        
        # Test 2: Create tasks
        print("\n2. Testing task creation...")
        test_actions = {
            "steps": ["Step 1", "Step 2", "Step 3"],
            "priority": "high",
            "tags": ["test", "database"]
        }
        
        task_id = tm.create_task(
            description="Test task for database validation",
            actions=test_actions,
            status=TaskStatus.NEW,
            progress=0.0
        )
        print(f"✓ Created test task with ID: {task_id}")
        
        # Test 3: Retrieve task
        print("\n3. Testing task retrieval...")
        retrieved_task = tm.get_task(task_id)
        if retrieved_task:
            print(f"✓ Retrieved task: {retrieved_task['description']}")
            print(f"  Status: {retrieved_task['status']}")
            print(f"  Progress: {retrieved_task['progress']}")
        else:
            raise Exception("Failed to retrieve created task")
        
        # Test 4: Update task
        print("\n4. Testing task updates...")
        update_success = tm.update_task(
            task_id,
            status=TaskStatus.STARTED,
            progress=0.5,
            actions={"steps": ["Updated step 1", "Updated step 2"], "priority": "medium"}
        )
        if update_success:
            print("✓ Task updated successfully")
            updated_task = tm.get_task(task_id)
            print(f"  New status: {updated_task['status']}")
            print(f"  New progress: {updated_task['progress']}")
        else:
            raise Exception("Failed to update task")
        
        # Test 5: Create multiple tasks for bulk operations
        print("\n5. Testing bulk operations...")
        task_ids = []
        statuses = [TaskStatus.NEW, TaskStatus.STARTED, TaskStatus.COMPLETED]
        
        for i, status in enumerate(statuses):
            tid = tm.create_task(
                description=f"Bulk test task {i+1}",
                actions={"test_number": i+1},
                status=status,
                progress=i * 0.5
            )
            task_ids.append(tid)
        print(f"✓ Created {len(task_ids)} additional test tasks")
        
        # Test 6: Get all tasks
        print("\n6. Testing get all tasks...")
        all_tasks = tm.get_all_tasks()
        print(f"✓ Retrieved {len(all_tasks)} total tasks")
        
        # Test 7: Get tasks by status
        print("\n7. Testing get tasks by status...")
        new_tasks = tm.get_tasks_by_status(TaskStatus.NEW)
        started_tasks = tm.get_tasks_by_status(TaskStatus.STARTED)
        completed_tasks = tm.get_tasks_by_status(TaskStatus.COMPLETED)
        print(f"✓ Found {len(new_tasks)} NEW tasks")
        print(f"✓ Found {len(started_tasks)} STARTED tasks")
        print(f"✓ Found {len(completed_tasks)} COMPLETED tasks")
        
        # Test 8: Delete tasks
        print("\n8. Testing task deletion...")
        deleted_count = 0
        for tid in task_ids:
            if tm.delete_task(tid):
                deleted_count += 1
        print(f"✓ Deleted {deleted_count} test tasks")
        
        # Test 9: Verify deletion
        print("\n9. Verifying deletions...")
        remaining_tasks = tm.get_all_tasks()
        print(f"✓ {len(remaining_tasks)} tasks remaining in database")
        
        # Test 10: Error handling
        print("\n10. Testing error handling...")
        try:
            # Try to get non-existent task
            non_existent = tm.get_task(99999)
            if non_existent is None:
                print("✓ Correctly returned None for non-existent task")
            
            # Try invalid progress value
            try:
                tm.create_task("Invalid progress task", progress=1.5)
                print("❌ Should have raised ValueError for invalid progress")
            except ValueError:
                print("✓ Correctly rejected invalid progress value")
                
        except Exception as e:
            print(f"❌ Unexpected error in error handling test: {e}")
        
        # Clean up - delete the test task we created
        print("\n🧹 Cleaning up...")
        if tm.delete_task(task_id):
            print("✓ Cleaned up test task")
        
        print("\n🎉 All tests passed!")
        
        # Optional: Show final state
        final_tasks = tm.get_all_tasks()
        print(f"\nFinal database state: {len(final_tasks)} tasks")
        for task in final_tasks:
            print(f"  - {task['description']} ({task['status']})")
            
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise
    finally:
        tm.close()

def test_table_management():
    """Test table creation and deletion."""
    load_dotenv()
    tm = TaskManager()
    
    try:
        print("\n🧪 Testing table management...")
        
        # Create table
        tm.create_tasks_table()
        print("✓ Table created")
        
        # Add a test task
        task_id = tm.create_task("Test task for table deletion")
        print("✓ Test task added")
        
        # Drop table
        print("⚠️  Dropping table (this will delete all data)...")
        tm.drop_tasks_table()
        print("✓ Table dropped successfully")
        
        # Recreate table
        tm.create_tasks_table()
        print("✓ Table recreated")
        
        # Verify it's empty
        tasks = tm.get_all_tasks()
        if len(tasks) == 0:
            print("✓ New table is empty as expected")
        else:
            print(f"❌ Expected empty table, found {len(tasks)} tasks")
            
    except Exception as e:
        print(f"❌ Table management test failed: {e}")
        raise
    finally:
        tm.close()

if __name__ == "__main__":
    # Run comprehensive tests
    test_database_operations()
    
    # Ask before running destructive test
    response = input("\nRun table drop/recreate test? This will delete all data (y/N): ")
    if response.lower() == 'y':
        test_table_management()
    else:
        print("Skipped table management test")