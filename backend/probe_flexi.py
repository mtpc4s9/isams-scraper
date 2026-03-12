import requests
from bs4 import BeautifulSoup

url = "https://support.flexischools.com.au/parents"
response = requests.get(url)

print(f"Status Code: {response.status_code}")

soup = BeautifulSoup(response.content, 'html.parser')

# Find categories inside the page
# Let's see if we have some distinct list of categories and links first.
print("--- Links inside ---")
links = soup.find_all('a', href=True)
count = 0
for l in links:
    if "hc/en-au/articles/" in l['href'] or "hc/en-us/articles/" in l['href'] or "support.flexischools.com.au/how-do-i" in l['href'] or "/articles/" in l['href']:
        print(f"{l.text.strip()} -> {l['href']}")
        count += 1
        if count > 20: break
    elif "hc/en-au/categories" in l['href'] or "hc/en-au/sections" in l['href'] or "#main-content" in l['href']:
        print(f"CATEGORY/SECTION: {l.text.strip()} -> {l['href']}")
