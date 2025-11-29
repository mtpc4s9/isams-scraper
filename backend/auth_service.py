from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        self.driver = None

    def get_driver(self):
        if not self.driver:
            options = Options()
            # options.add_argument("--headless") # Comment out for debugging
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        return self.driver

    def login(self, username, password):
        try:
            driver = self.get_driver()
            driver.get("https://identity.isams.com/")
            
            # Wait for redirect to login page
            WebDriverWait(driver, 15).until(
                EC.url_contains("/login/")
            )

            # Wait for login form elements to be ready
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "username"))
            )
            
            # Enter credentials
            username_field = driver.find_element(By.ID, "username")
            username_field.clear()
            username_field.send_keys(username)
            
            password_field = driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(password)
            
            # Click login
            login_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[class*='sfdc_button']"))
            )
            login_btn.click()
            
            # Wait for successful redirect or indicator
            # Adjust this selector based on actual post-login page
            time.sleep(5) # Temporary wait to ensure login processes
            
            # Check if we are still on login page or have error
            if "identity.isams.com" in driver.current_url and "error" in driver.page_source.lower():
                return False, "Login failed. Check credentials."
                
            return True, "Login successful"
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return False, f"Login error: {str(e)}"

    def open_login_page(self):
        driver = self.get_driver()
        try:
            driver.get("https://identity.isams.com/")
            return True, "Login page opened"
        except Exception as e:
            logger.error(f"Failed to open browser: {str(e)}")
            return False, f"Failed to open browser: {str(e)}"

    def check_authentication(self):
        if not self.driver:
            return False, "Browser not started"
        try:
            # Check if we are still on the login page
            # Login page usually has '/login/' in the URL
            current_url = self.driver.current_url
            if "/login/" not in current_url:
                 return True, "Authenticated"
            
            return False, f"Still on login page. Current URL: {current_url}"
        except Exception as e:
            return False, f"Error checking auth: {str(e)}"

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

auth_service = AuthService()
