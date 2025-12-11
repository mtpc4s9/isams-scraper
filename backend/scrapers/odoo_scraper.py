import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def scrape_odoo_article(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract Hierarchy from URL
        # Example: https://www.odoo.com/documentation/18.0/applications/sales/crm/acquire_leads/convert.html
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip('/').split('/')
        
        # Base path for Odoo 18 docs is usually documentation/18.0/
        # We want what comes after.
        try:
            start_index = path_parts.index('18.0') + 1
        except ValueError:
            start_index = 0 # Fallback
        
        relevant_parts = path_parts[start_index:]
        
        # Remove the file extension from the last part if it's an html file
        if relevant_parts and relevant_parts[-1].endswith('.html'):
            relevant_parts[-1] = relevant_parts[-1][:-5]
            
        levels = {}
        for i, part in enumerate(relevant_parts[:-1]): # All except last are levels
            levels[f"level_{i+1}"] = part.replace('_', ' ').title()
            
        # Article Name
        article_name = ""
        h1 = soup.find('h1')
        if h1:
            article_name = clean_text(h1.get_text())
            # Remove the pilcrow sign if present
            article_name = article_name.replace('¶', '').strip()
        else:
            article_name = relevant_parts[-1].replace('_', ' ').title()

        # Content
        main_content = soup.find('article', class_='doc-body') or soup.find('div', role='main')
        content_md = ""
        
        if main_content:
            # Use main_content as root. We will handle wrapper divs recursively in process_element.
            content_root = main_content

            def process_element(element, depth=2):
                md_out = ""
                if not element.name:
                    return ""
                    
                # Ignore git link
                if element.name == 'a' and 'o_git_link' in element.get('class', []):
                    return ""

                # Helper to check for alert classes
                classes = element.get('class', [])
                is_alert = any(cls.startswith('alert') for cls in classes)
                
                # Check for transparent wrappers (generic div)
                # If it's a div and NOT an alert, treat it as a wrapper and recurse
                if element.name == 'div' and not is_alert:
                    for child in element.children:
                        md_out += process_element(child, depth)
                    return md_out

                if element.name == 'section':
                    # Check for title
                    h_tag = element.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'], recursive=False)
                    if h_tag:
                        title = clean_text(h_tag.get_text()).replace('¶', '')
                        hashes = "#" * depth
                        md_out += f"{hashes} {title}\n\n"
                    
                    # Process children of section
                    for child in element.children:
                        md_out += process_element(child, depth + 1)
                        
                elif element.name == 'p':
                    text = clean_text(element.get_text())
                    if text:
                        md_out += f"{text}\n\n"
                        
                elif element.name == 'ul':
                    for li in element.find_all('li', recursive=False):
                        md_out += f"- {clean_text(li.get_text())}\n"
                    md_out += "\n"
                    
                elif element.name == 'ol':
                     for i, li in enumerate(element.find_all('li', recursive=False)):
                        md_out += f"{i+1}. {clean_text(li.get_text())}\n"
                     md_out += "\n"
                    
                elif element.name == 'div' and is_alert:
                     alert_type = "NOTE"
                     if 'alert-warning' in classes: alert_type = "WARNING"
                     elif 'alert-danger' in classes: alert_type = "CAUTION"
                     elif 'alert-info' in classes: alert_type = "NOTE"
                     elif 'alert-success' in classes: alert_type = "TIP"
                     
                     md_out += f"> [!{alert_type}]\n> {clean_text(element.get_text())}\n\n"
                
                # Fallback for standalone headers not inside section (rare but possible)
                elif element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                     title = clean_text(element.get_text()).replace('¶', '')
                     hashes = "#" * depth
                     md_out += f"{hashes} {title}\n\n"

                return md_out

            # Iterate over all children of content_root
            for child in content_root.children:
                content_md += process_element(child)
                         
        return {
            "url": url,
            "levels": levels,
            "article_name": article_name,
            "content": content_md
        }

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def _scrape_recursive(url, visited=None):
    if visited is None:
        visited = set()
    
    if url in visited:
        return []
    visited.add(url)
    
    articles_data = []
    
    # Check if it's a direct article (ends with .html)
    if url.endswith('.html'):
        data = scrape_odoo_article(url)
        if data:
            articles_data.append(data)
        return articles_data

    # Otherwise, treat as directory/category
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check for directory listing (Index of ...)
        if soup.title and "Index of" in soup.title.string:
            print(f"Scraping directory: {url}")
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                if href == '../' or href.startswith('?'): continue
                
                full_url = urljoin(url, href)
                
                if full_url.startswith(url): # Ensure we stay within the sub-path
                     # Recurse
                     articles_data.extend(_scrape_recursive(full_url, visited))
        
        else:
            # Standard Odoo Category Page (might list articles or sub-categories)
            # This part is tricky because standard pages link to everywhere.
            # We strictly follow the URL hierarchy provided by the user.
            # If the user gave .../essentials/, we look for .../essentials/foo/ or .../essentials/bar.html
            
            main_content = soup.find('article', class_='doc-body') or soup.find('div', role='main')
            if main_content:
                links = main_content.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    full_url = urljoin(url, href)
                    
                    # Strict check: child of current URL
                    if full_url.startswith(url) and full_url != url:
                         articles_data.extend(_scrape_recursive(full_url, visited))
                         
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        
    return articles_data

def scrape_odoo(url):
    print(f"Starting Odoo Scrape for: {url}")
    
    # Ensure URL ends with / if it's a directory to help logic (optional but good for consistency)
    if not url.endswith('.html') and not url.endswith('/'):
        url += '/'

    articles_data = _scrape_recursive(url)

    # Dedup just in case
    # Convert list of dicts to unique by URL
    seen_urls = set()
    unique_articles = []
    for art in articles_data:
        if art['url'] not in seen_urls:
            seen_urls.add(art['url'])
            unique_articles.append(art)
    
    articles_data = unique_articles
    print(f"Found {len(articles_data)} unique articles.")

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
