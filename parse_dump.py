from bs4 import BeautifulSoup
with open('topic_dump.html', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')
print('Expected count divs:')
for el in soup.select('div.value[aria-hidden=\"true\"]'):
    print(el.text)
print('\nArticle links (data-special-link):')
for a in soup.find_all('a', attrs={'data-special-link': 'true'}):
    print(a.get('href'))
print('\nAll article links (/s/article/):')
for a in soup.find_all('a', href=lambda x: x and '/s/article/' in x):
    print(a.get('href'))
