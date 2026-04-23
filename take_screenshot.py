import time
from backend.auth_service import AuthService

def take_screenshot():
    print("Taking screenshot of the topic page...")
    url = "https://help.classlink.com/s/topic/0TOUs0000000T0POAU/apps"
    auth = AuthService()
    try:
        driver = auth.get_driver(interactive=False, headless=False)
        driver.get(url)
        time.sleep(10)
        # Take a full page screenshot by scrolling
        # Actually just a regular screenshot is fine
        driver.save_screenshot("topic_page_screenshot.png")
        print("Saved screenshot to topic_page_screenshot.png")
    finally:
        auth.close()

if __name__ == "__main__":
    take_screenshot()
