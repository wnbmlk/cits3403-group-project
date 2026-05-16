import os
import tempfile
import threading
import unittest

from werkzeug.serving import make_server

from moviehub import create_app
from moviehub.extensions import db

try:
    from selenium import webdriver
    from selenium.common.exceptions import WebDriverException
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.common.by import By

    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class TestConfig:
    TESTING = True
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test-secret"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


@unittest.skipUnless(SELENIUM_AVAILABLE, "Selenium is not installed")
class SeleniumSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._db_fd, cls._db_path = tempfile.mkstemp(prefix="moviehub-selenium-", suffix=".db")

        class _RuntimeTestConfig(TestConfig):
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{cls._db_path}"

        cls.app = create_app(_RuntimeTestConfig)

        with cls.app.app_context():
            db.create_all()

        cls.server = make_server("127.0.0.1", 0, cls.app)
        cls.port = cls.server.server_port
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()

        options = ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        try:
            cls.driver = webdriver.Chrome(options=options)
        except WebDriverException as exc:
            raise unittest.SkipTest(f"Unable to start Chrome WebDriver: {exc}")

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "driver"):
            cls.driver.quit()

        if hasattr(cls, "server"):
            cls.server.shutdown()
            cls.server.server_close()

        with cls.app.app_context():
            db.session.remove()
            db.drop_all()

        os.close(cls._db_fd)
        os.unlink(cls._db_path)

    def test_homepage_loads_and_shows_movie_diary_heading(self):
        self.driver.get(f"http://127.0.0.1:{self.port}/")
        heading = self.driver.find_element(By.TAG_NAME, "h1")
        self.assertIn("Movie Diary", heading.text)

    def test_signup_page_contains_confirmation_password_input(self):
        self.driver.get(f"http://127.0.0.1:{self.port}/signup")
        confirm_input = self.driver.find_element(By.ID, "confirm_password")
        self.assertTrue(confirm_input.is_displayed())


if __name__ == "__main__":
    unittest.main()
