from bs4 import BeautifulSoup

with open("classlink_main.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

links = soup.find_all("a", href=True)
unique_links = {}
for i, l in enumerate(links):
    href = l['href']
    text = l.get_text(strip=True)
    if 's/' in href and len(href) > 20 and not text:
        # maybe an image link
        continue
    if href not in unique_links:
        unique_links[href] = text

for href, text in sorted(unique_links.items()):
    print(f"{href} | {text}")
