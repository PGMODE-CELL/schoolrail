"""
SchoolRail - Quick Test Script
Run this to verify the backend is working correctly
"""

import requests
import json

BASE_URL = "http://localhost:3001/api/v1"

def test_endpoints():
    print("Testing SchoolRail API Endpoints...\n")
    
    endpoints = [
        ("/vehicles", "GET"),
        ("/drivers", "GET"),
        ("/students", "GET"),
        ("/routes", "GET"),
        ("/attendance", "GET"),
        ("/fees", "GET"),
        ("/analytics/dashboard", "GET"),
    ]
    
    for endpoint, method in endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            if method == "GET":
                response = requests.get(url, timeout=2)
            else:
                response = requests.post(url, json={}, timeout=2)
            
            status = "✓" if response.status_code == 200 else "✗"
            print(f"{status} {method} {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"✗ {method} {endpoint} - Error: {str(e)[:50]}")

if __name__ == "__main__":
    test_endpoints()