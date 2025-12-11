import requests
from bs4 import BeautifulSoup

url = "https://www.odoo.com/documentation/18.0/applications/sales/crm/acquire_leads/convert.html"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

with open('odoo_structure.txt', 'w', encoding='utf-8') as f:
    # Try to find the main content
    main_content = soup.find('main') or soup.find('article') or soup.find(class_='document') or soup.find(id='wrap')

    if main_content:
        f.write("Found main content:\n")
        f.write(main_content.prettify()[:5000]) # Increased limit
        
        # Check for breadcrumbs
        breadcrumbs = soup.find(class_='breadcrumb') or soup.find(class_='o_breadcrumb') or soup.select_one('ol.breadcrumb')
        if breadcrumbs:
            f.write("\n\nFound breadcrumbs:\n")
            f.write(breadcrumbs.prettify())
    else:
        f.write("Could not find main content container.")
