import requests
from bs4 import BeautifulSoup
import sys

url = "https://support.flexischools.com.au/how-do-i-update-my-personal-information"
# Using a headers dictionary to simulate a browser visit
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers)
print(f"Status Code: {response.status_code}")
if response.status_code != 200:
    print("Failed to fetch")
    sys.exit(1)

soup = BeautifulSoup(response.content, 'html.parser')

# Title
title_elem = soup.find('h1')
title = title_elem.text.strip() if title_elem else "No Title"

# Content
# Let's try to find the main article body. Often it's a div with 'article-body' or 'content' class.
content_elem = soup.find('div', class_='article__body') or soup.find('article') or soup.find('main')
content = content_elem.text.strip()[:200] if content_elem else "No Content"

# Related articles
# They are usually in a sidebar or bottom section
related_articles = []
# Let's look for sections that might be related articles.
related_section = soup.find('section', class_='recent-articles') or soup.find('section', class_='related-articles') 
if not related_section:
    # Try finding an aside or a block with related links.
    for h3 in soup.find_all(['h2', 'h3']):
        if h3.text and 'related' in h3.text.lower():
            ul = h3.find_next_sibling('ul')
            if ul:
                related_section = ul
                break

if related_section:
    links = related_section.find_all('a')
    for link in links:
        related_articles.append(link.text.strip())

print(f"Title: {title}")
print(f"Content Length: {len(content) if content else 0}")
print(f"Related Articles: {'; '.join(related_articles)}")

# Try to look at all h2/h3 and links for related articles if not found
if not related_articles:
    print("Looking for related articles explicitly...")
    for section in soup.find_all('section'):
        h3 = section.find('h3')
        if h3 and 'related articles' in h3.text.lower():
            for a in section.find_all('a'):
                print(f"Found related: {a.text.strip()}")
