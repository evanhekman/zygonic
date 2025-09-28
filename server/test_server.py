"""
# Test the root endpoint
curl http://127.0.0.1:8000/

# Test POST endpoint with JSON body
curl -X POST "http://127.0.0.1:8000/new" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Create a Notion page about AI",
    "actions": [
      {
        "integration": "notion",
        "action": "create", 
        "args": {"title": "AI Notes", "content": "Notes about AI"},
        "webhook": "NOTION_WEBHOOK"
      }
    ],
    "status": "NEW",
    "progress": 0.0
  }'

# Test simple GET endpoint (easier for testing)
curl "http://127.0.0.1:8000/new-simple?description=Test%20task&status=NEW&progress=0.0"

# Test with actions in GET endpoint
curl -G "http://127.0.0.1:8000/new-simple" \
  --data-urlencode "description=Create Notion page" \
  --data-urlencode 'actions=[{"integration":"notion","action":"create","args":{"title":"Test"},"webhook":"WEBHOOK_URL"}]' \
  --data-urlencode "status=NEW" \
  --data-urlencode "progress=0.0"

# Test with invalid data (should return 400)
curl -X POST "http://127.0.0.1:8000/new" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Test task",
    "progress": 1.5
  }'
"""

import pytest
import requests
import json
from typing import Dict, Any

# Base URL for your FastAPI server
BASE_URL = "http://127.0.0.1:8000"

class TestTaskAPI:
    """Test suite for the task creation API"""
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        assert response.json() == {"message": "hello world"}
    
    def test_create_task_post_success(self):
        """Test successful task creation via POST"""
        task_data = {
            "description": "Test task from Python",
            "actions": [
                {
                    "integration": "notion",
                    "action": "create",
                    "args": {"title": "Test Page", "content": "Test content"},
                    "webhook": "TEST_WEBHOOK"
                }
            ],
            "status": "NEW",
            "progress": 0.0
        }
        
        response = requests.post(
            f"{BASE_URL}/new",
            json=task_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["status_code"] == 200
        assert "task_id" in result
        assert "message" in result
        print(f"Created task with ID: {result['task_id']}")
    
    def test_create_task_get_simple_success(self):
        """Test successful task creation via GET (simple endpoint)"""
        params = {
            "description": "Simple test task",
            "actions": json.dumps([{
                "integration": "slack",
                "action": "send_message",
                "args": {"channel": "#test", "message": "Hello"},
                "webhook": "SLACK_WEBHOOK"
            }]),
            "status": "NEW",
            "progress": 0.5
        }
        
        response = requests.get(f"{BASE_URL}/new-simple", params=params)
        assert response.status_code == 200
        result = response.json()
        assert result["status_code"] == 200
        assert "task_id" in result
    
    def test_invalid_progress(self):
        """Test validation of progress field"""
        task_data = {
            "description": "Test task with invalid progress",
            "progress": 1.5  # Invalid: > 1.0
        }
        
        response = requests.post(
            f"{BASE_URL}/new",
            json=task_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400
        assert "Progress must be between 0.0 and 1.0" in response.json()["detail"]
    
    def test_invalid_status(self):
        """Test validation of status field"""
        task_data = {
            "description": "Test task with invalid status",
            "status": "INVALID_STATUS"
        }
        
        response = requests.post(
            f"{BASE_URL}/new",
            json=task_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400
        assert "Invalid status" in response.json()["detail"]
    
    def test_invalid_actions_json_in_get(self):
        """Test invalid JSON in actions parameter for GET endpoint"""
        params = {
            "description": "Test task",
            "actions": "invalid json"  # Invalid JSON
        }
        
        response = requests.get(f"{BASE_URL}/new-simple", params=params)
        assert response.status_code == 400
        assert "Invalid JSON in actions parameter" in response.json()["detail"]
    
    def test_missing_description(self):
        """Test missing required description field"""
        task_data = {
            "status": "NEW",
            "progress": 0.0
            # Missing description
        }
        
        response = requests.post(
            f"{BASE_URL}/new",
            json=task_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_empty_actions(self):
        """Test task with empty actions list"""
        task_data = {
            "description": "Task with no actions",
            "actions": [],
            "status": "NEW",
            "progress": 0.0
        }
        
        response = requests.post(
            f"{BASE_URL}/new",
            json=task_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["status_code"] == 200

def run_manual_tests():
    """Run tests manually without pytest"""
    test_instance = TestTaskAPI()
    
    tests = [
        ("Root endpoint", test_instance.test_root_endpoint),
        ("POST task creation", test_instance.test_create_task_post_success),
        ("GET simple task creation", test_instance.test_create_task_get_simple_success),
        ("Invalid progress", test_instance.test_invalid_progress),
        ("Invalid status", test_instance.test_invalid_status),
        ("Invalid actions JSON", test_instance.test_invalid_actions_json_in_get),
        ("Missing description", test_instance.test_missing_description),
        ("Empty actions", test_instance.test_empty_actions),
    ]
    
    print("Running API tests...")
    print("=" * 50)
    
    for test_name, test_func in tests:
        try:
            print(f"Running: {test_name}...")
            test_func()
            print(f"✅ {test_name} PASSED")
        except Exception as e:
            print(f"❌ {test_name} FAILED: {str(e)}")
        print("-" * 30)

if __name__ == "__main__":
    # Make sure your server is running on http://127.0.0.1:8000
    print("Make sure your FastAPI server is running with: python server.py")
    input("Press Enter to continue with tests...")
    
    # Run tests manually
    run_manual_tests()
    
    print("\nTo run with pytest:")
    print("pip install pytest requests")
    print("pytest test_server.py -v")
