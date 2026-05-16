"""Selenium acceptance tests for user workflows."""
import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


@pytest.fixture
def driver():
    """Create and configure Chrome WebDriver for testing."""
    chrome_options = Options()
    # Comment out next line to see the browser window (visible mode)
    # chrome_options.add_argument("--headless")  # Uncomment for invisible browser
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(10)
    driver.implicitly_wait(5)
    
    yield driver
    driver.quit()


@pytest.fixture
def app_server():
    """Flask server should already be running on port 5001."""
    return "http://localhost:5001"


class TestUserSignupFlow:
    """Test user signup flow."""
    
    def test_signup_page_loads(self, driver, app_server):
        """Test signup page loads and displays form."""
        driver.get(f"{app_server}/signup")
        
        # Wait for page title or form to be visible
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )
        
        # Verify signup page is loaded
        assert "signup" in driver.current_url or "Signup" in driver.page_source or "sign up" in driver.page_source.lower()


class TestUserLoginFlow:
    """Test user login flow."""
    
    def test_login_page_loads(self, driver, app_server):
        """Test login page loads and displays form."""
        driver.get(f"{app_server}/login")
        
        # Wait for login form
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        
        assert driver.current_url == f"{app_server}/login"


class TestHomePage:
    """Test homepage functionality."""
    
    def test_homepage_loads(self, driver, app_server):
        """Test homepage loads without errors."""
        driver.get(f"{app_server}/")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        assert driver.current_url == f"{app_server}/" or driver.current_url == app_server
        assert "Movie" in driver.page_source or "Diary" in driver.page_source


class TestAboutPage:
    """Test about page."""
    
    def test_about_page_loads(self, driver, app_server):
        """Test about page loads."""
        driver.get(f"{app_server}/about")
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        assert driver.current_url == f"{app_server}/about"


class TestNavigationAndPages:
    """Test page navigation."""
    
    def test_all_pages_accessible(self, driver, app_server):
        """Test that key pages are accessible without errors."""
        pages = [
            ("/", "home"),
            ("/about", "about"),
            ("/signup", "signup"),
            ("/login", "login"),
        ]
        
        for path, name in pages:
            driver.get(f"{app_server}{path}")
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Verify no 404 or 500 errors in page source
            page_source = driver.page_source.lower()
            assert "404" not in page_source, f"404 error on {name} page"
            assert "500" not in page_source, f"500 error on {name} page"
