from scrapers.odoo_scraper import scrape_odoo
from scrapers.prompting_guide_scraper import scrape_prompting_guide

def test_odoo():
    url = "https://www.odoo.com/documentation/18.0/applications/sales/crm/acquire_leads/convert.html"
    print(f"Testing Odoo Scraper with {url}...")
    try:
        result = scrape_odoo(url)
        if result and "Convert leads into opportunities" in result:
            print("SUCCESS: Odoo Scraper returned content.")
            print(result[:200]) # Print first 200 chars
        else:
            print("FAILURE: Odoo Scraper returned empty or incorrect content.")
            print(result)
    except Exception as e:
        print(f"ERROR: {e}")

def test_prompting():
    url = "https://www.promptingguide.ai/introduction/basics"
    print(f"\nTesting Prompting Guide Scraper with {url}...")
    try:
        result = scrape_prompting_guide(url)
        if result and "Basics of Prompting" in result:
            print("SUCCESS: Prompting Guide Scraper returned content.")
            print(result[:200])
        else:
            print("FAILURE: Prompting Guide Scraper returned empty or incorrect content.")
            print(result)
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_odoo()
    test_prompting()
