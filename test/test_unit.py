import os
import tempfile
import unittest

from werkzeug.security import generate_password_hash

from moviehub import create_app
from moviehub.extensions import db
from moviehub.models import User


class TestConfig:
    TESTING = True
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test-secret"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class AuthUnitTests(unittest.TestCase):
    def setUp(self):
        self._db_fd, self._db_path = tempfile.mkstemp(prefix="moviehub-test-", suffix=".db")

        class _RuntimeTestConfig(TestConfig):
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{self._db_path}"

        self.app = create_app(_RuntimeTestConfig)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

        os.close(self._db_fd)
        os.unlink(self._db_path)

    def test_signup_creates_user_and_redirects_to_profile(self):
        response = self.client.post(
            "/signup",
            data={
                "username": "alice",
                "password": "StrongPass1!",
                "confirm_password": "StrongPass1!",
            },
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/profile", response.headers.get("Location", ""))

        with self.app.app_context():
            user = User.query.filter_by(username="alice").first()
            self.assertIsNotNone(user)
            self.assertNotEqual(user.password, "StrongPass1!")

    def test_signup_rejects_mismatched_confirmation(self):
        response = self.client.post(
            "/signup",
            data={
                "username": "bob",
                "password": "StrongPass1!",
                "confirm_password": "WrongPass1!",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Passwords do not match", response.data)

    def test_login_rejects_invalid_credentials(self):
        with self.app.app_context():
            db.session.add(User(username="charlie", password=generate_password_hash("StrongPass1!")))
            db.session.commit()

        response = self.client.post(
            "/login",
            data={"username": "charlie", "password": "BadPass1!"},
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Invalid credentials", response.data)


if __name__ == "__main__":
    unittest.main()
