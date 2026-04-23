import requests
from bs4 import BeautifulSoup
import re

url = 'https://community.instructure.com/en/kb/categories/95-administrators'
headers = {'User-Agent':'Mozilla/5.0'}
r = requests.get(url, headers=headers)
soup = BeautifulSoup(r.text, 'html.parser')
links = soup.find_all('a', href=re.compile(r'/kb/articles/'))

for a in links[:5]:
    print(a.text.strip(), a['href'])
