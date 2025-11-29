from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

print("Testing Chrome Driver installation...")
try:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    print("Driver initialized successfully.")
    driver.get("https://google.com")
    print("Browser opened successfully.")
    time.sleep(3)
    driver.quit()
    print("Test passed!")
except Exception as e:
    print(f"Test failed: {str(e)}")
