import time
import os
import logging
from backend.auth_service import AuthService

logging.basicConfig(level=logging.INFO)

def login_to_classlink():
    print("Mở trình duyệt để đăng nhập ClassLink...")
    print("Vui lòng đăng nhập vào tài khoản của bạn trên trình duyệt hiện lên.")
    print("Sau khi đăng nhập xong, hãy đóng trình duyệt hoặc nhấn Ctrl+C ở đây.")
    
    auth = AuthService()
    try:
        # Launching browser interactively
        driver = auth.get_driver(interactive=True, headless=False)
        driver.get("https://launchpad.classlink.com/ishcmc")
        
        # Keep it open for user to log in manually
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nĐã đóng trình duyệt.")
    finally:
        auth.close()

if __name__ == "__main__":
    login_to_classlink()
