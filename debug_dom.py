import sys
import os
import time

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.scraper_service import scraper_service

def debug_dom():
    url = "https://support.toddleapp.com/en/articles/8611858-how-can-i-configure-staff-access-permissions"
    print(f"Debugging DOM for: {url}")
    
    # Get the driver and fetch the page manually to dump HTML
    from auth_service import auth_service
    driver = auth_service.get_driver()
    driver.get(url)
    time.sleep(5)  # Plenty of time
    
    html = driver.page_source
    with open('toddle_debug.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("DONE: HTML saved to toddle_debug.html")
    
    # Also run the scrape to see current result
    success, message, articles, markdown = scraper_service.scrape_category(url)
    print("\nCURRENT SCRAPE RESULT:")
    print(markdown)

if __name__ == "__main__":
    debug_dom()
