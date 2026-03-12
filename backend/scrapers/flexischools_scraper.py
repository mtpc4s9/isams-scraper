import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
import markdownify
import re

base_url = "https://support.flexischools.com.au"

def get_markdown_for_article(article_url, title, related_titles, role=""):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(article_url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return f"- Article name: {title}\n- Article link: {article_url}\n- Role: {role}\n- Content: Error fetching content ({str(e)})\n- Related articles: {'; '.join(related_titles)}\n---\n"

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Try finding the article body
    content_div = soup.find('div', class_='article__body')
    if not content_div:
        content_div = soup.find('article') or soup.find('main')
    
    if content_div:
        # Better extraction using markdownify
        content_text = markdownify.markdownify(str(content_div), heading_style="ATX").strip()
        # Clean up excessive newlines
        content_text = re.sub(r'\n{3,}', '\n\n', content_text)
    else:
        content_text = "Content not found."

    # Format output
    md = f"- Article name: {title}\n"
    md += f"- Article link: {article_url}\n"
    md += f"- Role: {role}\n"
    md += f"- Content:\n{content_text}\n"
    if related_titles:
        md += f"\n- Related articles: {'; '.join(related_titles)}\n"
    md += "---\n"
    return md
def scrape_flexischools_category(category_url: str):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(category_url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return f"Error fetching {category_url}: {str(e)}"
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    sections = {}
    
    # Find all groupings. Zendesk often groups by h2 or h3 followed by a list <ul>
    headings = soup.find_all(['h2', 'h3'])
    for h in headings:
        section_name = h.text.strip()
        if not section_name:
            continue
            
        next_tag = h.find_next_sibling()
        while next_tag and next_tag.name not in ['ul', 'h2', 'h3']:
            next_tag = next_tag.find_next_sibling()
            
        if next_tag and next_tag.name == 'ul':
            links_elem = next_tag.find_all('a', href=True)
            articles = []
            for a in links_elem:
                title = a.text.strip()
                href = a['href']
                # absolute url
                if not href.startswith('http'):
                    href = urljoin(base_url, href)
                if title and href:
                    articles.append((title, href))
            if articles:
                sections[section_name] = articles

    if not sections:
        return "No sections/articles found on the provided page. Please check the URL."

    # Determine role from URL
    role = ""
    target_segment = category_url.split('/')[-1].split('?')[0].split('#')[0]
    if target_segment:
        role = target_segment
        
    # Now scrape all compiled articles
    full_markdown = f"# Flexischools Category Guidelines\nSource: {category_url}\nRole Context: {role}\n\n"
    overall_count = 0
    
    for section_name, articles in sections.items():
        # Get all titles in this section to serve as related articles
        section_titles = [a[0] for a in articles]
        
        full_markdown += f"## Category: {section_name}\n\n"
        
        for idx, (title, href) in enumerate(articles):
            related = [t for t in section_titles if t != title]
            
            md_article = get_markdown_for_article(href, title, related, role)
            full_markdown += md_article + "\n\n"
            overall_count += 1
            
            time.sleep(0.5)  # slight delay to be polite
            
    return full_markdown
