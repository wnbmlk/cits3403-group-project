"""Unit tests for diary functionality."""
import pytest
from datetime import datetime
from moviehub.models import DiaryEntry, Movie, User


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
                date=datetime.utcnow(),
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
