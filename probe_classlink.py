import time
import os
from backend.auth_service import AuthService

def probe_pages():
    auth = AuthService()
    driver = auth.get_driver(interactive=True, headless=False)
    
    if not driver:
        print("Failed to get driver.")
        return
        
    try:
        urls = [
            ("https://help.classlink.com/s/launchpad-home", "classlink_applet.html", 10),
            ("https://help.classlink.com/s/article/LoggingIn", "classlink_article.html", 5)
        ]
        
        for url, filename, wait_time in urls:
            print(f"Fetching {url}...")
            driver.get(url)
            time.sleep(wait_time) # allow rendering / auth token passing
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print(f"Saved {filename}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        auth.close()

if __name__ == "__main__":
    probe_pages()
