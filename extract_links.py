import sys
import os
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from auth_service import auth_service

def extract_links():
    url = "https://support.toddleapp.com/en/articles/8611858-how-can-i-configure-staff-access-permissions"
    print(f"Extracting breadcrumb links from: {url}")
    
    driver = auth_service.get_driver()
    driver.get(url)
    time.sleep(5)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Toddle/Intercom breadcrumbs
    breadcrumb_els = soup.select('.intercom-breadcrumb a, .breadcrumb a, [data-testid="breadcrumb"] a, nav a')
    
    print("\n--- BREADCRUMB LINKS FOUND ---")
    for a in breadcrumb_els:
        text = a.get_text().strip()
        link = urljoin(url, a.get('href'))
        print(f"Text: {text} | Link: {link}")

if __name__ == "__main__":
    extract_links()
