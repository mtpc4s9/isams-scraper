import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.scraper_service import scraper_service

def verify_user_target():
    url = "https://support.toddleapp.com/en/articles/8611858-how-can-i-configure-staff-access-permissions"
    print(f"Verifying Toddle target for: {url}")
    
    # We use scraping service which should use the authenticated driver
    success, message, articles, markdown = scraper_service.scrape_category(url)
    
    if success:
        print("\n--- FINAL MARKDOWN OUTPUT ---")
        print(markdown)
        
        # Check for specific fields
        print("\n--- VALIDATION CHECK ---")
        expected_entity = "School administrators"
        expected_topic = "Getting started"
        
        if expected_entity in markdown:
            print(f"SUCCESS: Found '{expected_entity}'")
        else:
            print(f"WARNING: '{expected_entity}' NOT FOUND.")
            
        if expected_topic in markdown:
            print(f"SUCCESS: Found '{expected_topic}'")
        else:
            print(f"WARNING: '{expected_topic}' NOT FOUND.")
            
        # Check for line separation
        if "Entity: " in markdown and "\n\nTopic: " in markdown:
            print("SUCCESS: Line separation detected.")
        else:
            print("WARNING: Formatting might still be condensed.")
    else:
        print(f"FAILURE: {message}")

if __name__ == "__main__":
    verify_user_target()
