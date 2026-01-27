import sys
import os
import time

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.scrapers.toddle_scraper import ToddleScraper
from auth_service import auth_service
from bs4 import BeautifulSoup

def verify_verbose():
    url = "https://support.toddleapp.com/en/collections/7053659-getting-started"
    driver = auth_service.get_driver()
    scraper = ToddleScraper(driver)
    
    print(f"Fetching collection: {url}")
    driver.get(url)
    time.sleep(5)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    topics = scraper._extract_topics_and_articles(soup, "Getting started")
    
    print(f"\nDiscovered Topics: {list(topics.keys())}")
    
    for topic, links in topics.items():
        print(f"Topic '{topic}' has {len(links)} links.")
        if links:
            print(f"Sample link: {links[0]}")
            # Try to scrape the first one manually
            print(f"Attempting to scrape first article: {links[0][1]}")
            data = scraper.scrape_article(links[0][1], "Getting started", topic)
            if data:
                print("SUCCESS: Scraped data for first article.")
                print(f"Title: {data['article']}")
            else:
                print("FAILURE: Could not scrape first article.")

if __name__ == "__main__":
    verify_verbose()
