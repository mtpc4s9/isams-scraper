import time
import logging
from backend.auth_service import AuthService

logging.basicConfig(level=logging.INFO)

def login_and_navigate():
    """Open Chrome with saved profile so user can SSO login, then navigate to test article."""
    print("Opening browser for ClassLink SSO login...")
    print("Please log in, then press Enter here when ready.")
    
    auth = AuthService()
    try:
        driver = auth.get_driver(interactive=True, headless=False)
        driver.get("https://help.classlink.com/s/article/onesync-advanced-settings-enable-auto-correlation")
        
        input("\n>>> Press Enter after you have logged in successfully... ")
        print("Browser stays open. You can now run the debug script.")
        
    except KeyboardInterrupt:
        print("\nCancelled.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    login_and_navigate()
