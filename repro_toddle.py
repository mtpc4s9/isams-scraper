import sys
import os
from bs4 import BeautifulSoup

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.scrapers.toddle_scraper import ToddleScraper

class MockDriver:
    def __init__(self, html):
        self.page_source = html
    def get(self, url):
        pass

def test_repro():
    # Mocking the HTML structure of a Toddle article
    html = """
    <html>
        <body>
            <nav class="intercom-breadcrumb">
                <a href="/">Home</a>
                <a href="/collections/1">School administrators</a>
                <a href="/collections/1/topics/2">Getting started</a>
            </nav>
            <article>
                <h1>How do I sign in to my admin account on web?</h1>
                <div class="intercom-article-body">
                    <p>To sign in, go to the website and enter your credentials.</p>
                    <ul>
                        <li>Step 1</li>
                        <li>Step 2</li>
                    </ul>
                </div>
            </article>
        </body>
    </html>
    """
    driver = MockDriver(html)
    scraper = ToddleScraper(driver)
    
    url = "https://support.toddleapp.com/en/articles/8611848-how-do-i-sign-in-to-my-admin-account-on-web"
    result = scraper.scrape_article(url)
    
    print("--- SCRAPE RESULT ---")
    import json
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test_repro()
