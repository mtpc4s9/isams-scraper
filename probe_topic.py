import sys
from backend.auth_service import AuthService
from backend.scrapers.classlink_scraper import ClassLinkScraper
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

def test_topic(url):
    auth = AuthService()
    driver = auth.get_driver(interactive=True, headless=True)
    
    if not driver:
        print("Failed to get driver.")
        return
        
    try:
        scraper = ClassLinkScraper(driver)
        # We just want to test topic scraping logic
        print(f"Loading {url} ...")
        driver.get(url)
        import time
        time.sleep(5)
        
        # Test getting expected count
        expected_count = scraper._get_expected_article_count()
        print(f"Expected count: {expected_count}")
        
        # Test expand all
        scraper._expand_all_articles(expected_count)
        
        # Test collect links
        links = scraper._collect_article_links()
        print(f"Collected {len(links)} links:")
        for link in links:
            print(" -", link)
            
        with open("topic_dump.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        auth.close()

if __name__ == "__main__":
    url = "https://help.classlink.com/s/topic/0TOUs0000000XGvOAM/profiles-groups-users"
    test_topic(url)
