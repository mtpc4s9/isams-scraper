import requests
from bs4 import BeautifulSoup

url = "https://ps.powerschool-docs.com/pssis-admin/latest/get-started"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

print("=== START OF PROBE ===")
nav = soup.find('nav')
if nav:
    print("Found <nav> tag. Contents preview:")
    print(nav.prettify()[:1000])

import re
get_started = soup.find(string=re.compile("Get Started"))
if get_started:
    print(f"\nFound 'Get Started'. Tag: {get_started.parent.name}, classes: {get_started.parent.get('class')}")
    parent = get_started.parent
    for _ in range(4):
        parent = parent.parent
        if not parent: break
        print(f"Parent tag: {parent.name}, classes: {parent.get('class')}")

# Try to look for a known Son like "Staff Current Schedule"
son = soup.find(string=re.compile("Staff Current Schedule"))
if son:
    print(f"\nFound 'Staff Current Schedule'. Tag: {son.parent.name}, classes: {son.parent.get('class')}")
else:
    print("\nDid not find 'Staff Current Schedule' on this page directly (might be dynamically loaded or in a collapsed menu).")
print("=== END OF PROBE ===")
