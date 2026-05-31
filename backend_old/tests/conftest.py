import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def test_db():
    return "sqlite:///./test_schoolrail.db"

@pytest.fixture
def test_client():
    from fastapi.testclient import TestClient
    from main import app
    return TestClient(app)

@pytest.fixture
def mock_school():
    return {
        "name": "Test School",
        "address": "Test Address",
        "phone": "+1234567890",
        "email": "test@school.com"
    }

@pytest.fixture
def mock_vehicle():
    return {
        "vehicle_number": "TEST123",
        "vehicle_type": "bus",
        "capacity": 50,
        "status": "active"
    }

@pytest.fixture
def mock_driver():
    return {
        "name": "Test Driver",
        "phone": "+1234567890",
        "license_number": "DL123456",
        "status": "active"
    }

@pytest.fixture
def mock_student():
    return {
        "name": "Test Student",
        "student_id": "STU001",
        "parent_phone": "+1234567890"
    }