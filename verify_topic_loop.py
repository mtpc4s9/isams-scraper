import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.scraper_service import scraper_service

def verify_topic_loop():
    # We'll test the "Getting started" collection directly since it's most likely what the user wanted
    # as their screenshot showed 4 articles in this section.
    url = "https://support.toddleapp.com/en/collections/7053659-getting-started"
    print(f"Verifying Topic Loop Crawl for: {url}")
    
    success, message, articles, markdown = scraper_service.scrape_category(url)
    
    if success:
        print(f"\nSUCCESS: Scraped {len(articles)} articles.")
        if articles:
            print("\n--- ARTICLES FOUND ---")
            for i, a in enumerate(articles[:5]):
                print(f"{i+1}. {a['article']} ({a['topic']})")
        
        if len(articles) > 1:
            print(f"\nSUCCESS: Loop crawling verified.")
        else:
            print("\nWARNING: Only found 1 or 0 articles. Extraction might be missing links.")
    else:
        print(f"FAILURE: {message}")

if __name__ == "__main__":
    verify_topic_loop()
