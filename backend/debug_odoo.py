from scrapers.odoo_scraper import scrape_odoo
import requests
from bs4 import BeautifulSoup

url = "https://www.odoo.com/documentation/18.0/applications/essentials/"

print(f"Testing Odoo Scraper with {url}...")
try:
    # First, let's just print what the scraper sees
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    main_content = soup.find('article', class_='doc-body') or soup.find('div', role='main')
    
    if main_content:
        print("Main content found.")
        links = main_content.find_all('a', href=True)
        print(f"Found {len(links)} links in main content.")
        for link in links[:5]:
            print(f" - {link['href']}")
    else:
        print("Main content NOT found.")
        print(soup.prettify()[:1000])

    # Now run the actual function
    result = scrape_odoo(url)
    if result:
        print("\nScraper Result Length:", len(result))
    else:
        print("\nScraper Result is Empty/None")

except Exception as e:
    print(f"ERROR: {e}")
