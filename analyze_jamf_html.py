from bs4 import BeautifulSoup
import re

def peek_jamf_html():
    with open("jamf_article_dump.html", "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
        
    print("--- h1 tags ---")
    for h in soup.find_all("h1"):
        print(h.get_text(strip=True))
        
    print("\n--- h2 tags ---")
    for h in soup.find_all("h2")[:5]:
        print(h.get_text(strip=True))

    print("\n--- title ---")
    if soup.title:
        print(soup.title.string)

    print("\n--- Trying to find 'LDAP' ---")
    ldap_nodes = soup.find_all(string=re.compile("LDAP", re.IGNORECASE))
    for node in ldap_nodes[:10]:
        print(repr(node.parent.name), repr(node.strip()))
        
    print("\n--- Trying to find navigation elements ---")
    navs = soup.find_all(['nav', 'div'], class_=lambda c: c and 'nav' in c.lower())
    print([n.get('class') for n in navs[:5]])

if __name__ == "__main__":
    peek_jamf_html()
