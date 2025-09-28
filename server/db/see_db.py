#!/usr/bin/env python3
"""
Quick script to view the contents of the tasks database
"""

from db import TaskManager
import json
from datetime import datetime

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

def main():
    print("=" * 80)
    print("DATABASE CONTENTS")
    print("=" * 80)
    
    try:
        # Create TaskManager instance
        task_mgr = TaskManager()
        
        # Get all tasks (limited to 100 by the query)
        tasks = task_mgr.get_all_tasks()
        
        if not tasks:
            print("No tasks found in database.")
            return
        
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
                print("action:")
                if isinstance(task['action'], dict):
                    for key, action in task['action'].items():
                        if isinstance(action, dict):
                            print(f"  {key}: {action.get('integration', 'N/A')}.{action.get('action', 'N/A')}")
                            if action.get('args'):
                                args = action['args']
                                # Show key args
                                for arg_key, arg_value in list(args.items())[:3]:  # Show first 3 args
                                    display_value = truncate_text(str(arg_value), 50)
                                    print(f"    {arg_key}: {display_value}")
                                if len(args) > 3:
                                    print(f"    ... and {len(args) - 3} more args")
                        else:
                            print(f"  {key}: {truncate_text(str(action), 60)}")
                else:
                    print(f"  {truncate_text(str(task['action']), 60)}")
            else:
                print("action: None")
            
            print()  # Empty line between tasks
            
            # Break after 100 entries
            if i >= 100:
                print(f"... (showing first 100 entries)")
                break
        
        print("=" * 80)
        print(f"Total tasks shown: {min(len(tasks), 100)}")
        
    except Exception as e:
        print(f"Error accessing database: {e}")
        return 1
    
    finally:
        try:
            task_mgr.close()
        except:
            pass

if __name__ == "__main__":
    exit(main())