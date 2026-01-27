import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.scraper_service import scraper_service

def verify_topic_crawl():
    # Target URL for "Getting started" topic
    url = "https://support.toddleapp.com/en/collections/3653139-school-administrators#getting-started"
    print(f"Verifying Topic Crawl for: {url}")
    
    success, message, articles, markdown = scraper_service.scrape_category(url)
    
    if success:
        print(f"\nSUCCESS: Scraped {len(articles)} articles.")
        print("\n--- FORMATTING PREVIEW ---")
        # Print the first few hundred characters to check line separation
        print(markdown[:1000])
        
        # Check for expected field structure
        if "Entity: School administrators" in markdown:
            print("\nSUCCESS: 'Entity: School administrators' found.")
        else:
            print("\nWARNING: Hierarchy might still be off.")
            
        if "\n\nTopic:" in markdown and "\n\nArticle:" in markdown:
            print("SUCCESS: Explicit line separation (double newline) detected.")
    else:
        print(f"FAILURE: {message}")

if __name__ == "__main__":
    verify_topic_crawl()
