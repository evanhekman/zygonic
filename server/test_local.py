import json
import os
import tempfile
import shutil
from dataclasses import dataclass, asdict
from typing import Dict, Any
import unittest
from webhook import local_webhook, process_file, process_terminal

@dataclass
class Action:
    """Represents an action that can be executed by the AI agent"""
    integration: str
    action: str
    description: str
    args: Dict[str, Any]
    webhook: str
    
    def serialize(self) -> str:
        """Serialize action to JSON string"""
        return json.dumps(asdict(self), indent=2)
    
    @classmethod
    def deserialize(cls, json_str: str) -> 'Action':
        """Deserialize action from JSON string"""
        data = json.loads(json_str)
        return cls(**data)
    
    def execute(self) -> Dict[str, Any]:
        """Execute the action using the local webhook system"""
        return local_webhook(
            integration=self.integration,
            action=self.action,
            args=self.args,
            webhook=self.webhook
        )

class TestActions(unittest.TestCase):
    
    def setUp(self):
        """Set up temporary directory for testing"""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test_file.py")
        
    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_terminal_execute_action(self):
        """Test terminal execute action"""
        print("\n=== Testing Terminal Execute Action ===")
        
        # Define the action
        terminal_action = Action(
            integration="terminal",
            action="execute", 
            description="Creates a directory and a simple Python file",
            args={
                "command": f"mkdir -p {os.path.join(self.test_dir, 'src')} && echo 'print(\"Hello from terminal!\")' > {os.path.join(self.test_dir, 'src', 'hello.py')}",
                "working_dir": self.test_dir
            },
            webhook="TERMINAL"
        )
        
        # Test serialization
        serialized = terminal_action.serialize()
        print(f"Serialized: {serialized}")
        
        # Test deserialization
        deserialized = Action.deserialize(serialized)
        self.assertEqual(terminal_action.integration, deserialized.integration)
        self.assertEqual(terminal_action.action, deserialized.action)
        self.assertEqual(terminal_action.args, deserialized.args)
        print("✓ Serialization/deserialization successful")
        
        # Execute the action
        result = deserialized.execute()
        print(f"Execution result: {result}")
        
        # Verify execution
        self.assertTrue(result.get("success", False), f"Command failed: {result}")
        self.assertEqual(result.get("return_code"), 0)
        
        # Verify file was created
        created_file = os.path.join(self.test_dir, 'src', 'hello.py')
        self.assertTrue(os.path.exists(created_file), "File was not created by terminal command")
        print("✓ Terminal action executed successfully")
    
    def test_file_modify_action(self):
        """Test file modify action"""
        print("\n=== Testing File Modify Action ===")
        
        # Define the action
        file_modify_action = Action(
            integration="file",
            action="modify",
            description="Creates a Python file with specific content",
            args={
                "filepath": self.test_file,
                "content": '''#!/usr/bin/env python3
"""
Test file created by file modify action
"""

def main():
    print("Hello from file modify!")
    return "success"

if __name__ == "__main__":
    main()
'''
            },
            webhook="FILES"
        )
        
        # Test serialization
        serialized = file_modify_action.serialize()
        print(f"Serialized length: {len(serialized)} characters")
        
        # Test deserialization
        deserialized = Action.deserialize(serialized)
        self.assertEqual(file_modify_action.integration, deserialized.integration)
        self.assertEqual(file_modify_action.action, deserialized.action)
        self.assertEqual(file_modify_action.args["filepath"], deserialized.args["filepath"])
        print("✓ Serialization/deserialization successful")
        
        # Execute the action
        result = deserialized.execute()
        print(f"Execution result: {result}")
        
        # Verify execution
        self.assertTrue(result.get("success", False), f"File modify failed: {result}")
        self.assertTrue(os.path.exists(self.test_file), "File was not created")
        
        # Verify content
        with open(self.test_file, 'r') as f:
            content = f.read()
            self.assertIn("Hello from file modify!", content)
            self.assertIn("def main():", content)
        print("✓ File modify action executed successfully")
    
    def test_file_open_action(self):
        """Test file open action"""
        print("\n=== Testing File Open Action ===")
        
        # First create a file to open
        with open(self.test_file, 'w') as f:
            f.write("# Test file for opening\nprint('This file will be opened in VSCode')\n")
        
        # Define the action
        file_open_action = Action(
            integration="file",
            action="open",
            description="Opens a file in VSCode",
            args={
                "filepath": self.test_file
            },
            webhook="FILES"
        )
        
        # Test serialization
        serialized = file_open_action.serialize()
        print(f"Serialized: {serialized}")
        
        # Test deserialization
        deserialized = Action.deserialize(serialized)
        self.assertEqual(file_open_action.integration, deserialized.integration)
        self.assertEqual(file_open_action.action, deserialized.action)
        self.assertEqual(file_open_action.args, deserialized.args)
        print("✓ Serialization/deserialization successful")
        
        # Execute the action
        result = deserialized.execute()
        print(f"Execution result: {result}")
        
        # Note: This might fail if VSCode is not installed or not in PATH
        # We'll check for both success and the specific VSCode error
        if result.get("success"):
            self.assertTrue(result.get("success"))
            print("✓ File open action executed successfully")
        else:
            # Check if it's a VSCode-related error (acceptable for testing)
            error_msg = result.get("error", "")
            if "code command" in error_msg or "VSCode" in error_msg:
                print("⚠ VSCode not available in test environment (expected)")
                self.assertIn("VSCode", error_msg)
            else:
                self.fail(f"Unexpected error: {result}")
    
    def test_error_handling(self):
        """Test error handling for invalid actions"""
        print("\n=== Testing Error Handling ===")
        
        # Test invalid terminal command
        invalid_terminal = Action(
            integration="terminal",
            action="execute",
            description="Invalid command test",
            args={
                "command": "nonexistent_command_xyz_123",
                "working_dir": self.test_dir
            },
            webhook="TERMINAL"
        )
        
        result = invalid_terminal.execute()
        print(f"Invalid command result: {result}")
        self.assertFalse(result.get("success", True))
        self.assertNotEqual(result.get("return_code"), 0)
        print("✓ Invalid terminal command handled correctly")
        
        # Test file operation on invalid path
        invalid_file = Action(
            integration="file",
            action="open",
            description="Open non-existent file",
            args={
                "filepath": "/nonexistent/path/file.txt"
            },
            webhook="FILES"
        )
        
        result = invalid_file.execute()
        print(f"Invalid file result: {result}")
        self.assertIsNotNone(result.get("error"))
        print("✓ Invalid file operation handled correctly")
    
    def test_integrated_workflow(self):
        """Test a complete workflow using multiple actions"""
        print("\n=== Testing Integrated Workflow ===")
        
        project_name = "test_project"
        project_dir = os.path.join(self.test_dir, project_name)
        
        # Step 1: Create project structure
        setup_action = Action(
            integration="terminal",
            action="execute",
            description="Set up project structure",
            args={
                "command": f"mkdir -p {project_name}/src {project_name}/tests",
                "working_dir": self.test_dir
            },
            webhook="TERMINAL"
        )
        
        result1 = setup_action.execute()
        self.assertTrue(result1.get("success"), f"Setup failed: {result1}")
        print("✓ Step 1: Project structure created")
        
        # Step 2: Create main.py file
        main_file = os.path.join(project_dir, "src", "main.py")
        create_main = Action(
            integration="file",
            action="modify",
            description="Create main.py",
            args={
                "filepath": main_file,
                "content": '''#!/usr/bin/env python3

def greet(name):
    return f"Hello, {name}!"

def main():
    print(greet("World"))

if __name__ == "__main__":
    main()
'''
            },
            webhook="FILES"
        )
        
        result2 = create_main.execute()
        self.assertTrue(result2.get("success"), f"Main file creation failed: {result2}")
        print("✓ Step 2: main.py created")
        
        # Step 3: Create test file
        test_file = os.path.join(project_dir, "tests", "test_main.py") 
        create_test = Action(
            integration="file",
            action="modify",
            description="Create test file",
            args={
                "filepath": test_file,
                "content": '''import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import greet

def test_greet():
    assert greet("Test") == "Hello, Test!"
    print("✓ Test passed")

if __name__ == "__main__":
    test_greet()
'''
            },
            webhook="FILES"
        )
        
        result3 = create_test.execute()
        self.assertTrue(result3.get("success"), f"Test file creation failed: {result3}")
        print("✓ Step 3: test file created")
        
        # Step 4: Run the test
        run_test = Action(
            integration="terminal",
            action="execute",
            description="Run the test",
            args={
                "command": "python tests/test_main.py",
                "working_dir": project_dir
            },
            webhook="TERMINAL"
        )
        
        result4 = run_test.execute()
        self.assertTrue(result4.get("success"), f"Test execution failed: {result4}")
        self.assertIn("Test passed", result4.get("stdout", ""))
        print("✓ Step 4: Test executed successfully")
        
        print("✓ Complete workflow executed successfully!")

if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)