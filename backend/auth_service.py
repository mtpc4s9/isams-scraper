from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        self.driver = None
        self.project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.user_data_dir = os.path.join(self.project_dir, 'chrome_profile')

    def get_driver(self, interactive=False):
        # Check if existing driver is still alive
        if self.driver:
            try:
                _ = self.driver.current_url
                return self.driver
            except:
                try: self.driver.quit()
                except: pass
                self.driver = None
        
        options = Options()
        options.add_argument(f"--user-data-dir={self.user_data_dir}")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        if interactive:
            options.add_experimental_option("detach", True)
        else:
            # options.add_argument("--headless") # Headless would lose the session if not careful
            pass
            
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        return self.driver

    def launch_login(self, target_url="https://support.toddleapp.com/"):
        """Launch a persistent browser window for the user to log in."""
        try:
            driver = self.get_driver(interactive=True)
            driver.get(target_url)
            logger.info(f"Persistent browser opened at {target_url}")
            return True, "Persistent browser opened for login"
        except Exception as e:
            logger.error(f"Failed to launch login: {e}")
            return False, str(e)

    def check_authentication(self):
        if not self.driver:
            return False, "Browser not started"
        try:
            current_url = self.driver.current_url
            if "login" not in current_url.lower():
                return True, "Authenticated"
            return False, f"Likely on login page: {current_url}"
        except Exception as e:
            self.driver = None
            return False, str(e)

    def close(self):
        if self.driver:
            try: self.driver.quit()
            except: pass
            self.driver = None

auth_service = AuthService()
