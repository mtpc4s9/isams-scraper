import requests
from bs4 import BeautifulSoup

url = "https://www.odoo.com/documentation/18.0/applications/essentials/contacts/merge.html"

try:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    print("--- Title ---")
    print(soup.title)
    
    print("\n--- H1 ---")
    print(soup.find('h1'))
    
    print("\n--- Potential Content Containers ---")
    # Check for common Odoo classes
    doc_body = soup.find('article', class_='doc-body')
    print(f"article.doc-body found: {doc_body is not None}")
    
    main_role = soup.find('div', role='main')
    print(f"div[role='main'] found: {main_role is not None}")
    
    main_tag = soup.find('main')
    print(f"main tag found: {main_tag is not None}")
    
    # If doc-body is found, let's look at its direct children
    if doc_body:
        print("\n--- direct children of doc-body ---")
        for child in doc_body.find_all(recursive=False):
            print(f"Tag: {child.name}, Class: {child.get('class')}")
            # Print first few chars of content
            text = child.get_text()[:50].replace('\n', ' ')
            print(f"   Content snippet: {text}...")

    elif main_role:
         print("\n--- direct children of div[role='main'] ---")
         for child in main_role.find_all(recursive=False):
            print(f"Tag: {child.name}, Class: {child.get('class')}")

except Exception as e:
    print(e)
