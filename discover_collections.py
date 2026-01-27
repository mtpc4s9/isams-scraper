import sys
import os
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from auth_service import auth_service

def discover_collections():
    url = "https://support.toddleapp.com/en/"
    print(f"Discovering collections from: {url}")
    
    driver = auth_service.get_driver()
    driver.get(url)
    time.sleep(10) 
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Intercom collection links
    collection_links = soup.find_all('a', href=lambda h: h and '/collections/' in h)
    
    print("\n--- COLLECTIONS FOUND ---")
    if not collection_links:
        print("No collection links found. Dumping HTML for analysis.")
        with open('home_debug.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
    else:
        for a in collection_links:
            text = a.get_text().strip()
            link = urljoin(url, a.get('href'))
            print(f"Text: {text} | Link: {link}")

if __name__ == "__main__":
    discover_collections()
