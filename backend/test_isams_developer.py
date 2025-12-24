from scrapers.isams_developer_scraper import scrape_isams_developer
from auth_service import auth_service
import time

def test_developer_docs():
    # This assumes the user has already logged in via the UI/browser
    # For a purely automated test, we would need to call auth_service.login() 
    # but the user provided credentials might have MFA or session nuances.
    # We will try to use the current driver session.
    
    url = "https://developer.isams.com/isams-developer-documentation/docs/batch-api"
    print(f"Testing iSAMS Developer Scraper with {url}...")
    
    driver = auth_service.get_driver()
    
    # Check if we are logged in - if not, we might need to login first for the test
    # But since this is a local environment, the agent can use the providing creds
    # if necessary. However, better to assume session exists if possible.
    
    try:
        # Check if we need to login
        driver.get(url)
        time.sleep(3)
        if "identity.isams.com" in driver.current_url:
            print("Not logged in. Attempting login...")
            auth_service.login("truongpcm@renaissance.edu.vn", "*@MinhTruong3186")
            driver.get(url)
            time.sleep(3)

        result = scrape_isams_developer(url, driver)
        if result and "Batch API" in result:
            print("SUCCESS: iSAMS Developer Scraper returned content.")
            print(f"Content Length: {len(result)}")
            
            # Save to file with explicit encoding
            import io
            import sys
            # Ensure stdout handles utf-8 for printing if possible, but mainly focus on the file
            with io.open("dev_docs_test.md", "w", encoding="utf-8") as f:
                f.write(result)
            print("Saved results to dev_docs_test.md")
        else:
            print("FAILURE: iSAMS Developer Scraper returned empty or incorrect content.")
            # Avoid printing complex characters to console if it might fail
            # print(result) 
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_developer_docs()
