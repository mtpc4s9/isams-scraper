import requests
from bs4 import BeautifulSoup
import re

url = 'https://community.instructure.com/en/kb/articles/387045-account-and-sub-account-role-comparison'
headers = {'User-Agent':'Mozilla/5.0'}
r = requests.get(url, headers=headers)
soup = BeautifulSoup(r.text, 'html.parser')
article_body = soup.find('div', class_=re.compile(r'article-body|content|message-body'))
if article_body:
    print(article_body.text[:500])
else:
    print("Could not find article body")
