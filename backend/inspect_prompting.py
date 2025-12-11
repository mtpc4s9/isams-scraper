import requests
from bs4 import BeautifulSoup

url = "https://www.promptingguide.ai/introduction/basics"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

with open('prompting_structure.txt', 'w', encoding='utf-8') as f:
    # Try to find the main content
    main_content = soup.find('main') or soup.find('article') or soup.find(class_='nextra-content')

    if main_content:
        f.write("Found main content:\n")
        f.write(main_content.prettify()[:5000])
    else:
        f.write("Could not find main content container.")
