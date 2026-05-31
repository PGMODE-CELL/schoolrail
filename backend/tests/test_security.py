import pytest
from app.core.security import (
    verify_password, get_password_hash, create_access_token,
    decode_token, get_user, authenticate_user
)


class TestSecurity:
    def test_password_hashing(self):
        password = "testpassword123"
        hashed = get_password_hash(password)
        assert hashed != password
        assert verify_password(password, hashed) is True
    
    def test_password_verification_wrong(self):
        password = "testpassword123"
        hashed = get_password_hash(password)
        assert verify_password("wrongpassword", hashed) is False
    
    def test_create_and_decode_token(self):
        data = {"sub": 1, "username": "testuser", "role": "admin"}
        token = create_access_token(data)
        assert token is not None
        
        decoded = decode_token(token)
        assert decoded.username == "testuser"
        assert decoded.role == "admin"
    
    def test_get_user(self):
        user = get_user("admin")
        assert user is not None
        assert user.username == "admin"
    
    def test_get_user_not_found(self):
        user = get_user("nonexistent")
        assert user is None
    
    def test_authenticate_user_valid(self):
        user = authenticate_user("admin", "admin123")
        assert user is not None
        assert user.username == "admin"
    
    def test_authenticate_user_invalid_password(self):
        user = authenticate_user("admin", "wrongpassword")
        assert user is None
    
    def test_authenticate_user_not_found(self):
        user = authenticate_user("nonexistent", "password")
        assert user is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
