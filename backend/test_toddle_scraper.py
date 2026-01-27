"""
Test script for Toddle Scraper
This script demonstrates how to use the Toddle scraper directly.

Requirements:
1. User must manually log in to https://support.toddleapp.com first
2. The browser session will be reused for scraping

Usage:
    python test_toddle_scraper.py
"""

from auth_service import auth_service
from scrapers.toddle_scraper import scrape_toddle
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("=" * 70)
    print("TODDLE DOCUMENTATION SCRAPER - TEST")
    print("=" * 70)
    
    # Step 1: Open browser for manual login
    print("\n[STEP 1] Opening browser for manual login...")
    success, message = auth_service.open_login_page()
    if not success:
        print(f"Error: {message}")
        return
    
    print(f"✓ {message}")
    print("\n📌 IMPORTANT: Please navigate to https://support.toddleapp.com and log in manually")
    print("   Press Enter when you have successfully logged in...")
    input()
    
    # Step 2: Get authenticated driver
    driver = auth_service.get_driver()
    if not driver:
        print("❌ Error: Could not get driver")
        return
    
    print("\n✓ Driver ready")
    
    # Step 3: Test URLs
    test_urls = [
        # Single collection
        "https://support.toddleapp.com/en/collections/8595214-educators",
        
        # Single article (uncomment to test)
        # "https://support.toddleapp.com/en/articles/8612033-how-do-i-sign-in-to-my-educator-account-on-web",
    ]
    
    for url in test_urls:
        print("\n" + "=" * 70)
        print(f"[STEP 2] Testing URL: {url}")
        print("=" * 70)
        
        try:
            markdown = scrape_toddle(url, driver)
            
            # Save to file
            filename = f"toddle_output_{url.split('/')[-1]}.md"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(markdown)
            
            print(f"\n✓ Scraping completed!")
            print(f"✓ Output saved to: {filename}")
            print(f"\nPreview (first 500 chars):")
            print("-" * 70)
            print(markdown[:500])
            print("-" * 70)
            
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
            logger.exception(e)
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    
    # Keep browser open for inspection
    print("\nThe browser will remain open for inspection.")
    print("Press Enter to close the browser and exit...")
    input()
    
    auth_service.close()
    print("✓ Browser closed. Goodbye!")

if __name__ == "__main__":
    main()
