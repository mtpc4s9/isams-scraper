import time
import os
import logging
from backend.auth_service import AuthService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO)

script = """
function extractText() {
    // Try to get text directly
    let el = document.querySelector('.component-main, #designed-reader-content, body');
    if (el) return el.innerText;
    return "Not found";
}
return extractText();
"""

def probe_again():
    auth = AuthService()
    try:
        driver = auth.get_driver(headless=False)
        article_url = "https://learn.jamf.com/r/en-US/jamf-pro-documentation-current/Google_Secure_LDAP_Integration"
        driver.get(article_url)
        
        # Click cookie consent if present
        try:
            btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            btn.click()
            print("Accepted cookies via #onetrust-accept-btn-handler")
            time.sleep(2)
        except Exception:
            pass

        # Wait up to 15 seconds for .ft-title or content inside designed-reader-content
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1, .ft-title"))
            )
        except Exception:
            pass
            
        time.sleep(2)

        # Print all text found
        text = driver.execute_script(script)
        with open("jamf_text2.txt", "w", encoding="utf-8") as f:
            f.write(text)
        print("Saved jamf_text2.txt length:", len(text))
        
        # Also dump HTML again
        with open("jamf_dump2.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        auth.close()

if __name__ == "__main__":
    probe_again()
