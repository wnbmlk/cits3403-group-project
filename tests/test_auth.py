"""Unit tests for authentication and user management."""
import pytest
from moviehub.models import User
from werkzeug.security import check_password_hash


class TestSignup:
    """Test user signup functionality."""
    
    def test_signup_valid_credentials(self, client, test_user_dict):
        """Test successful signup with valid credentials."""
        response = client.post(
            "/signup",
            data=test_user_dict,
            follow_redirects=True
        )
        assert response.status_code == 200
        
        # Verify user was created
        user = User.query.filter_by(username="newuser").first()
        assert user is not None
        assert check_password_hash(user.password, "SecurePass123!")
    
    def test_signup_duplicate_username(self, client, test_user, test_user_dict):
        """Test signup fails with duplicate username."""
        # Try to create user with same name as test_user
        data = test_user_dict.copy()
        data["username"] = "testuser"
        
        response = client.post("/signup", data=data)
        assert response.status_code == 200
        
        # Check error message displayed
        assert b"already taken" in response.data or b"exists" in response.data or b"Username" in response.data
        
        # Verify no duplicate was created
        users = User.query.filter_by(username="testuser").all()
        assert len(users) == 1
    
    def test_signup_weak_password(self, client, test_user_dict):
        """Test signup fails with weak password."""
        data = test_user_dict.copy()
        data["password"] = "weak"
        data["confirm_password"] = "weak"
        
        response = client.post("/signup", data=data)
        assert response.status_code == 200
        
        # Check error message displayed
        assert b"password" in response.data.lower()
        
        # Verify user not created
        user = User.query.filter_by(username="newuser").first()
        assert user is None
    
    def test_signup_password_mismatch(self, client, test_user_dict):
        """Test signup fails when passwords don't match."""
        data = test_user_dict.copy()
        data["confirm_password"] = "Different123!"
        
        response = client.post("/signup", data=data)
        assert response.status_code == 200
        
        # Check error message displayed
        assert b"match" in response.data.lower() or b"password" in response.data.lower()


class TestLogin:
    """Test user login functionality."""
    
    def test_login_valid_credentials(self, client, test_user):
        """Test successful login with valid credentials."""
        response = client.post(
            "/login",
            data={"username": "testuser", "password": "TestPassword123!"},
            follow_redirects=True
        )
        assert response.status_code == 200
        
        # Check user is redirected to home (logged in)
        assert b"Movie Diary" in response.data or b"Diary" in response.data
    
    def test_login_invalid_username(self, client):
        """Test login fails with non-existent username."""
        response = client.post(
            "/login",
            data={"username": "nonexistent", "password": "AnyPassword123!"}
        )
        assert response.status_code == 200
        
        # Check error message displayed
        assert b"Invalid" in response.data or b"incorrect" in response.data or b"Login" in response.data
    
    def test_login_invalid_password(self, client, test_user):
        """Test login fails with incorrect password."""
        response = client.post(
            "/login",
            data={"username": "testuser", "password": "WrongPassword123!"}
        )
        assert response.status_code == 200
        
        # Check error message displayed
        assert b"Invalid" in response.data or b"incorrect" in response.data


class TestPasswordValidation:
    """Test password strength validation."""
    
    def test_password_strength_api(self, client):
        """Test password strength API endpoint."""
        response = client.post(
            "/api/password-strength",
            json={"password": "WeakPass1"}
        )
        assert response.status_code == 200
        
        data = response.get_json()
        assert "score" in data
        assert isinstance(data["score"], int)
        assert 0 <= data["score"] <= 5
    
    def test_strong_password_scores_high(self, client):
        """Test strong password gets high score."""
        response = client.post(
            "/api/password-strength",
            json={"password": "VerySecurePassword123!@#"}
        )
        data = response.get_json()
        assert data["score"] >= 4
    
    def test_weak_password_scores_low(self, client):
        """Test weak password gets low score."""
        response = client.post(
            "/api/password-strength",
            json={"password": "weak"}
        )
        data = response.get_json()
        assert data["score"] <= 2
