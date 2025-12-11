import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def scrape_prompting_guide_article(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract Hierarchy from URL
        # Example: https://www.promptingguide.ai/introduction/basics
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip('/').split('/')
        
        levels = {}
        for i, part in enumerate(path_parts[:-1]):
            levels[f"level_{i+1}"] = part.replace('-', ' ').title()
            
        # Article Name
        article_name = ""
        h1 = soup.find('h1')
        if h1:
            article_name = clean_text(h1.get_text())
        else:
            article_name = path_parts[-1].replace('-', ' ').title()

        # Content
        # Nextra uses <main>
        main_content = soup.find('main')
        content_md = ""
        
        if main_content:
            # We need to skip the breadcrumbs and title if they are inside main (sometimes they are)
            # Based on inspection, h1 is inside main. Breadcrumbs are also inside main.
            
            # Iterate over children of main
            # We want to skip the breadcrumb div
            
            for element in main_content.children:
                if element.name == 'div' and 'nextra-breadcrumb' in element.get('class', []):
                    continue
                if element.name == 'h1':
                    continue # Already got title
                
                # Process content elements
                if element.name == 'h2':
                    title = clean_text(element.get_text()).replace('#', '')
                    content_md += f"## {title}\n\n"
                elif element.name == 'h3':
                    title = clean_text(element.get_text()).replace('#', '')
                    content_md += f"### {title}\n\n"
                elif element.name == 'p':
                    content_md += f"{clean_text(element.get_text())}\n\n"
                elif element.name == 'ul':
                    for li in element.find_all('li'):
                        content_md += f"- {clean_text(li.get_text())}\n"
                    content_md += "\n"
                elif element.name == 'ol':
                    for i, li in enumerate(element.find_all('li')):
                        content_md += f"{i+1}. {clean_text(li.get_text())}\n"
                    content_md += "\n"
                elif element.name == 'div' and 'nextra-code-block' in element.get('class', []):
                    code = element.find('code')
                    if code:
                        lang = code.get('data-language', '')
                        code_text = code.get_text()
                        content_md += f"```{lang}\n{code_text}\n```\n\n"
                elif element.name == 'pre': # Sometimes pre is direct child
                    code = element.find('code')
                    if code:
                        lang = code.get('data-language', '')
                        code_text = code.get_text()
                        content_md += f"```{lang}\n{code_text}\n```\n\n"

        return {
            "url": url,
            "levels": levels,
            "article_name": article_name,
            "content": content_md
        }

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def scrape_prompting_guide(url):
    articles_data = []
    
    # Simple logic: Scrape the given URL.
    # If the user wants recursive, we might need to find links.
    # For now, let's treat it as a single article or try to find sub-links if it looks like a category.
    
    # First scrape the URL itself
    data = scrape_prompting_guide_article(url)
    if data:
        articles_data.append(data)
        
        # Check if it's a category page that lists other pages
        # In Nextra, usually the sidebar has the links, but we might not have easy access to sidebar if it's outside main.
        # But often index pages have cards or links to sub-pages in the main content.
        
        # Let's try to find links in the main content that are sub-paths of current URL
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            main_content = soup.find('main')
            
            if main_content:
                links = main_content.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    full_url = urljoin(url, href)
                    
                    # Heuristic: If full_url starts with url and is longer, it's a sub-page
                    if full_url.startswith(url) and full_url != url:
                         # Avoid anchors on same page
                         if '#' in full_url and full_url.split('#')[0] == url:
                             continue
                             
                         print(f"Found potential sub-article: {full_url}")
                         # Limit recursion depth or count? For now just one level deep
                         sub_data = scrape_prompting_guide_article(full_url)
                         if sub_data and sub_data['content'].strip(): # Only if it has content
                             articles_data.append(sub_data)
                             
        except Exception as e:
            print(f"Error finding sub-articles for {url}: {e}")

    # Format Output
    final_md = ""
    for article in articles_data:
        final_md += f"# {article['article_name']}\n"
        final_md += f"**Link**: {article['url']}\n"
        for k, v in article['levels'].items():
            final_md += f"**{k.replace('_', ' ').title()}**: {v}\n"
        final_md += "\n"
        final_md += article['content']
        final_md += "\n---\n\n"
        
    return final_md
