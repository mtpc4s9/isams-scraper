import os
import sys
import logging
from backend.auth_service import AuthService
from backend.scrapers.classlink_scraper import scrape_classlink

logging.basicConfig(level=logging.INFO)

def test_scraper():
    url = "https://help.classlink.com/s/topic/0TOUs0000000T0POAU/apps"
    auth = AuthService()
    try:
        driver = auth.get_driver(interactive=False, headless=False)
        articles, md = scrape_classlink(url, "Apps", driver)
        print(f"Scraped {len(articles)} articles!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        auth.close()

if __name__ == "__main__":
    test_scraper()
