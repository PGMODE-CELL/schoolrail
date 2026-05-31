import pytest
from fastapi.testclient import TestClient
from datetime import date, timedelta
from app.main import app

client = TestClient(app)


class TestAuthEndpoints:
    def test_login_success(self):
        response = client.post("/api/v1/auth/login/json", params={
            "username": "admin",
            "password": "admin123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self):
        response = client.post("/api/v1/auth/login/json", params={
            "username": "admin",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
    
    def test_get_current_user(self):
        login_response = client.post("/api/v1/auth/login/json", params={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        response = client.get("/api/v1/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert "username" in data


class TestVehicleEndpoints:
    def test_list_vehicles(self):
        login_response = client.post("/api/v1/auth/login/json", params={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        response = client.get("/api/v1/vehicles/", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_vehicle_by_id(self):
        login_response = client.post("/api/v1/auth/login/json", params={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        response = client.get("/api/v1/vehicles/1", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert "vehicle_number" in data
    
    def test_create_vehicle(self):
        login_response = client.post("/api/v1/auth/login/json", params={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        vehicle_data = {
            "vehicle_number": "DL-TEST-9999",
            "vehicle_type": "bus",
            "capacity": 40,
            "make": "Tata",
            "model": "Starbus",
            "year": 2024
        }
        
        response = client.post("/api/v1/vehicles/", json=vehicle_data, headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200


class TestDriverEndpoints:
    def test_list_drivers(self):
        login_response = client.post("/api/v1/auth/login/json", params={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        response = client.get("/api/v1/drivers/", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_driver_by_id(self):
        login_response = client.post("/api/v1/auth/login/json", params={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        response = client.get("/api/v1/drivers/1", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200


class TestStudentEndpoints:
    def test_list_students(self):
        login_response = client.post("/api/v1/auth/login/json", params={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        response = client.get("/api/v1/students/", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_student_by_id(self):
        login_response = client.post("/api/v1/auth/login/json", params={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        response = client.get("/api/v1/students/1", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200


class TestRouteEndpoints:
    def test_list_routes(self):
        login_response = client.post("/api/v1/auth/login/json", params={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        response = client.get("/api/v1/routes/", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_route_by_id(self):
        login_response = client.post("/api/v1/auth/login/json", params={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        response = client.get("/api/v1/routes/1", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200
    
    def test_optimize_route(self):
        login_response = client.post("/api/v1/auth/login/json", params={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        response = client.post("/api/v1/routes/1/optimize", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200


class TestAttendanceEndpoints:
    def test_get_daily_attendance(self):
        login_response = client.post("/api/v1/auth/login/json", params={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        today = date.today()
        response = client.get(f"/api/v1/attendance/daily?attendance_date={today}", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200
    
    def test_get_attendance_statistics(self):
        login_response = client.post("/api/v1/auth/login/json", params={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        response = client.get("/api/v1/attendance/statistics", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200


class TestFeeEndpoints:
    def test_get_fee_structures(self):
        login_response = client.post("/api/v1/auth/login/json", params={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        response = client.get("/api/v1/fees/structures", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200
    
    def test_get_student_fees(self):
        login_response = client.post("/api/v1/auth/login/json", params={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        response = client.get("/api/v1/fees/student/1", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200


class TestGPSEndpoints:
    def test_get_active_vehicles(self):
        login_response = client.post("/api/v1/auth/login/json", params={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        response = client.get("/api/v1/gps/active", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200
    
    def test_get_alerts(self):
        login_response = client.post("/api/v1/auth/login/json", params={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        response = client.get("/api/v1/gps/alerts", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200


class TestNotificationEndpoints:
    def test_get_notifications(self):
        login_response = client.post("/api/v1/auth/login/json", params={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        response = client.get("/api/v1/notifications/", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200
    
    def test_get_notification_stats(self):
        login_response = client.post("/api/v1/auth/login/json", params={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        response = client.get("/api/v1/notifications/stats", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200


class TestScanEndpoints:
    def test_scan_qr_code(self):
        login_response = client.post("/api/v1/auth/login/json", params={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        scan_data = {
            "qr_data": "SR_STU:1",
            "route_id": 1,
            "status": "present"
        }
        
        response = client.post("/api/v1/scan/qr", json=scan_data, headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200
    
    def test_scan_rfid_card(self):
        login_response = client.post("/api/v1/auth/login/json", params={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        scan_data = {
            "rfid_uid": "RFID001",
            "route_id": 1,
            "status": "present"
        }
        
        response = client.post("/api/v1/scan/rfid", json=scan_data, headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
