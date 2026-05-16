"""Test configuration and fixtures for pytest."""
import os
import tempfile
import pytest
from moviehub import create_app, db
from moviehub.models import User
from werkzeug.security import generate_password_hash


class TestConfig:
    """Test configuration: in-memory SQLite database."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test-secret-key"


@pytest.fixture
def app():
    """Create and configure test app with in-memory database."""
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        # Dispose engine to ensure all connections are closed and avoid ResourceWarning
        try:
            db.engine.dispose()
        except Exception:
            pass


@pytest.fixture
def client(app):
    """Test client for making requests."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLI runner for testing CLI commands."""
    return app.test_cli_runner()


@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = User(
            username="testuser",
            password=generate_password_hash("TestPassword123!")
        )
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def test_user_dict():
    """Test user credentials as dictionary."""
    return {
        "username": "newuser",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!"
    }


@pytest.fixture
def authenticated_client(client, test_user):
    """Client with authenticated session."""
    client.post("/login", data={
        "username": "testuser",
        "password": "TestPassword123!"
    }, follow_redirects=True)
    return client
