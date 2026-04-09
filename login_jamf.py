import time
import os
import logging
from backend.auth_service import AuthService

logging.basicConfig(level=logging.INFO)

def login_to_jamf():
    print("Mở trình duyệt để đăng nhập Jamf Learn...")
    print("Vui lòng đăng nhập vào tài khoản của bạn trên trình duyệt hiện lên.")
    
    auth = AuthService()
    try:
        # Launching browser interactively
        driver = auth.get_driver(interactive=True, headless=False)
        driver.get("https://learn.jamf.com/")
        
        input("\n>>> Nhấn phím Enter tại đây SAU KHI bạn đã đăng nhập thành công và trang web đã tải xong... ")
        print("Đang lưu session...")
            
    except Exception as e:
        print(f"\nLỗi: {e}")
    finally:
        auth.close()
        print("Đã đóng trình duyệt và lưu session. Bạn có thể sử dụng scraper bây giờ.")

if __name__ == "__main__":
    login_to_jamf()
