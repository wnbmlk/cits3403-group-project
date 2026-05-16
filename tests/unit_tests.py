"""Unit tests for authentication, user management, and diary functionality."""
import pytest
from datetime import datetime
from moviehub.models import User, DiaryEntry
from werkzeug.security import check_password_hash


# ============================================================================
# AUTHENTICATION AND SIGNUP TESTS
# ============================================================================

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


# ============================================================================
# DIARY ENTRY TESTS
# ============================================================================

class TestDiaryCreation:
    """Test diary entry creation."""
    
    def test_create_diary_entry(self, authenticated_client):
        """Test successful diary entry creation."""
        response = authenticated_client.post(
            "/api/diary/entries",
            json={
                "title": "Test Movie",
                "status": "Watched",
                "genre": "Action",
                "date": "2024-05-15"
            }
        )
        assert response.status_code == 201
        
        data = response.get_json()
        assert data["title"] == "Test Movie"
        assert data["status"] == "Watched"
        assert data["genre"] == "Action"
    
    def test_create_diary_entry_missing_title(self, authenticated_client):
        """Test diary entry creation fails without title."""
        response = authenticated_client.post(
            "/api/diary/entries",
            json={
                "status": "Watched",
                "genre": "Action",
                "date": "2024-05-15"
            }
        )
        assert response.status_code == 400
        
        data = response.get_json()
        assert "error" in data
    
    def test_create_diary_entry_invalid_status(self, authenticated_client):
        """Test diary entry creation fails with invalid status."""
        response = authenticated_client.post(
            "/api/diary/entries",
            json={
                "title": "Test Movie",
                "status": "InvalidStatus",
                "genre": "Action",
                "date": "2024-05-15"
            }
        )
        assert response.status_code == 400
        
        data = response.get_json()
        assert "error" in data


class TestDiaryRetrieval:
    """Test retrieving diary entries."""
    
    def test_get_diary_entries(self, authenticated_client):
        """Test retrieving user's diary entries via API."""
        # Use the authenticated client to get entries
        response = authenticated_client.get("/api/diary/entries")
        assert response.status_code == 200
        
        data = response.get_json()
        assert "entries" in data
        assert isinstance(data["entries"], list)
    
    def test_get_diary_entries_empty(self, authenticated_client):
        """Test retrieving diary entries when none exist."""
        response = authenticated_client.get("/api/diary/entries")
        assert response.status_code == 200
        
        data = response.get_json()
        assert "entries" in data
        assert isinstance(data["entries"], list)


class TestDiaryDeletion:
    """Test deleting diary entries."""
    
    def test_delete_nonexistent_entry(self, authenticated_client):
        """Test deleting non-existent diary entry returns 404."""
        response = authenticated_client.delete("/api/diary/entries/99999")
        assert response.status_code == 404
    
    def test_cannot_delete_other_users_entry(self, client, app):
        """Test user cannot delete another user's diary entry."""
        # Create two users
        other_user_id = None
        entry_id = None
        with app.app_context():
            from moviehub import db
            from werkzeug.security import generate_password_hash
            
            test_user = User(
                username="deletetest1",
                password=generate_password_hash("TestPass123!")
            )
            db.session.add(test_user)
            db.session.flush()
            test_user_id = test_user.id
            
            other_user = User(
                username="deletetest2",
                password=generate_password_hash("Password123!")
            )
            db.session.add(other_user)
            db.session.flush()
            other_user_id = other_user.id
            
            # Create entry for other_user
            entry = DiaryEntry(
                title="Other's Movie",
                status="Watched",
                media_type="Movie",
                genre="Action",
                date=datetime.now(),
                user_id=other_user_id
            )
            db.session.add(entry)
            db.session.commit()
            entry_id = entry.id
        
        # Login as test_user
        client.post(
            "/login",
            data={"username": "deletetest1", "password": "TestPass123!"},
            follow_redirects=True
        )
        
        # Try to delete other_user's entry
        response = client.delete(f"/api/diary/entries/{entry_id}")
        assert response.status_code == 403
