import pytest
from app.auth.utils import verify_password, get_password_hash, authenticate_user
from app.auth.models import UserInDB


def test_password_hashing():
    """Test password hashing and verification."""
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    assert verify_password(password, hashed) == True
    assert verify_password("wrongpassword", hashed) == False


def test_user_authentication():
    """Test user authentication."""
    # Test with valid credentials
    user = authenticate_user("testuser", "secret")
    assert user is not None
    assert user.username == "testuser"
    
    # Test with invalid credentials
    user = authenticate_user("testuser", "wrongpassword")
    assert user is None
    
    # Test with non-existent user
    user = authenticate_user("nonexistent", "password")
    assert user is None
