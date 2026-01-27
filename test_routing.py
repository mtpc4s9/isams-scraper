import sys
import os
import logging

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.scraper_service import scraper_service

logging.basicConfig(level=logging.INFO)

def test_routing():
    # Test Toddle URL delegation
    url = "https://support.toddleapp.com/en/articles/8611848-how-do-i-sign-in-to-my-admin-account-on-web"
    print(f"Testing routing for: {url}")
    
    # This should trigger the smart routing logic
    success, message, articles, markdown = scraper_service.scrape_category(url)
    
    print(f"Success: {success}")
    print(f"Message: {message}")
    if markdown:
        print(f"Markdown preview (first 100 chars): {markdown[:100]}...")

if __name__ == "__main__":
    test_routing()
