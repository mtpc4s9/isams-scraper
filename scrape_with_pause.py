import time
import logging
from backend.auth_service import AuthService
from backend.scrapers.classlink_scraper import scrape_classlink

logging.basicConfig(level=logging.INFO)

def run():
    auth = AuthService()
    try:
        # Open browser in foreground
        driver = auth.get_driver(interactive=False, headless=False)
        
        # Navigate to login page
        driver.get("https://myapps.classlink.com/")
        print("Browser is open and ready.")
        print("Please log in with your school email and SSO.")
        print("After logging in, navigate to the Help Center if needed.")
        
        # Wait for me to press Enter
        input("\n>>> [WAITING] Press Enter here once you are logged in... ")
        
        # Now do the scrape
        url = "https://help.classlink.com/s/topic/0TOUs0000000T0POAU/apps"
        print(f"\nStarting scrape for: {url}")
        
        # We also need to fix the Load More button XPath directly here or rely on classlink_scraper's current logic
        # For now, let's just see how many it finds. We can patch classlink_scraper.py afterwards if needed.
        articles, md = scrape_classlink(url, "Apps", driver)
        
        print(f"\nFinished! Scraped {len(articles)} articles.")
        
        with open("apps_topic.md", "w", encoding="utf-8") as f:
            f.write(md)
            print("Saved output to apps_topic.md")
            
    finally:
        auth.close()

if __name__ == "__main__":
    run()
