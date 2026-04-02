import sys
import logging
from backend.auth_service import AuthService
from backend.scrapers.classlink_scraper import scrape_classlink
import json

logging.basicConfig(level=logging.INFO)

def verify_fix():
    print("Testing extraction for ClassLink article...")
    url = "https://help.classlink.com/s/article/apptrack-admin-release-notes"
    
    auth = AuthService()
    try:
        # Use headless false to see if login is working, or let it use the existing saved profile
        driver = auth.get_driver(headless=False)
        articles, markdown = scrape_classlink(url, "AppTrack", driver)
        
        if not articles:
            print("Failed to scrape article.")
            return

        article = articles[0]
        print("\n--- EXTRACTION RESULTS ---")
        print(f"Product: {article.get('product')}")
        print(f"Audience: {article.get('audience')}")
        print(f"Article Name: {article.get('article_name')}")
        
        print("\nExpected:")
        print("Product: AppTrack")
        print("Audience: ClassLink Administrator")
        print("Article Name: AppTrack Admin Release Notes")

    except Exception as e:
        print(f"Error during verification: {e}")
    finally:
        auth.close()

if __name__ == "__main__":
    verify_fix()
