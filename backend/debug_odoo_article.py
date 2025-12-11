from scrapers.odoo_scraper import scrape_odoo_article
import requests
from bs4 import BeautifulSoup

url = "https://www.odoo.com/documentation/18.0/applications/essentials/activities.html"

print(f"Testing Odoo Article Scraper with {url}...")

# 1. Run the function
data = scrape_odoo_article(url)
if data:
    print(f"Article Name: {data['article_name']}")
    print(f"Content Length: {len(data['content'])}")
    print("Content Preview:")
    print(data['content'][:500])
else:
    print("Function returned None")

# 2. Inspect HTML if content is empty
if not data or not data['content']:
    print("\n--- Inspecting HTML ---")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    main_content = soup.find('article', class_='doc-body') or soup.find('div', role='main')
    if main_content:
        print("Main content container found.")
        print("First 1000 chars of main content:")
        print(main_content.prettify()[:1000])
        
        print("\nChecking sections:")
        sections = main_content.find_all('section', recursive=False)
        print(f"Found {len(sections)} top-level sections.")
    else:
        print("Main content container NOT found.")
        print("Body preview:")
        print(soup.body.prettify()[:1000] if soup.body else "No body tag")
