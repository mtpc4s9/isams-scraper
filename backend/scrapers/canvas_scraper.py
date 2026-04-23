import requests
from bs4 import BeautifulSoup
import re
import time
from markdownify import markdownify as md

def scrape_article(url: str) -> str:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            return ""
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # In Vanilla Knowledge Base, articles usually have a specific wrapper or just 'userContent'
        target = soup.find(class_='userContent')
        if not target:
            target = soup.find('div', class_='ArticleBody')
        if not target:
            # Fallback to finding h1 and getting its parent's parent
            h1 = soup.find('h1')
            if h1 and h1.parent and h1.parent.parent:
                target = h1.parent.parent
            else:
                target = soup.body
                
        # Remove navigation or unwanted elements if necessary
        for el in target.find_all(['nav', 'script', 'style', 'footer']):
            el.decompose()
            
        markdown_content = md(str(target), heading_style="ATX", escape_asterisks=False, escape_underscores=False)
        # Clean up excessive newlines
        markdown_content = re.sub(r'\n{3,}', '\n\n', markdown_content)
        return markdown_content.strip()
    except Exception as e:
        return f"> **Note:** Failed to parse article content. Error: {e}"

def scrape_canvas(url: str, category_name: str) -> str:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    # Extract group name from URL
    # e.g. https://community.instructure.com/en/kb/categories/454-instructors -> instructors -> Instructors
    # e.g. https://community.instructure.com/en/kb/canvas-lms-basics-guide -> canvas-lms-basics-guide -> Canvas Lms Basics Guide
    match = re.search(r'/(?:categories/\d+-|kb/)([^/]+?)(?:/p\d+)?(?:/)?$', url)
    if match:
        group_name = match.group(1).replace('-', ' ').title()
    else:
        group_name = "Unknown Group"
        
    page = 1
    articles_scraped = 0
    markdown_lines = []
    
    # Add metadata envelope per the skill requirements
    import datetime
    now_str = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
    
    markdown_lines.append("## Extraction Results")
    markdown_lines.append("")
    markdown_lines.append(f"**Source:** [Canvas LMS - {group_name}]({url})")
    markdown_lines.append(f"**Date:** {now_str}")
    markdown_lines.append("**Confidence:** HIGH")
    markdown_lines.append("**Strategy:** A (WebFetch)")
    markdown_lines.append("**Format:** Markdown Text")
    markdown_lines.append("")
    markdown_lines.append("---")
    markdown_lines.append("")
    
    global_seen_urls = set()
    
    while True:
        current_url = url if page == 1 else f"{url}/p{page}"
        try:
            r = requests.get(current_url, headers=headers, timeout=10)
        except requests.exceptions.RequestException as e:
            if articles_scraped == 0:
                return f"Error connecting to Canvas URL: {e}"
            break
            
        if r.status_code != 200:
            break
            
        if 'This category does not have any articles.' in r.text:
            break
            
        soup = BeautifulSoup(r.text, 'html.parser')
        # Extract links to articles
        links = soup.find_all('a', href=re.compile(r'/kb/articles/'))
        
        if not links:
            break
            
        # Filter and deduplicate links
        valid_links = []
        for a in links:
            href = a.get('href')
            if href and href not in global_seen_urls:
                global_seen_urls.add(href)
                
                # Determine sub-group if inside a <section> with <h3>
                sub_group = group_name
                section = a.find_parent('section')
                if section:
                    h3 = section.find('h3')
                    if h3 and h3.text:
                        sub_group = f"{group_name} - {h3.text.strip()}"
                
                valid_links.append((a.text.strip(), href, sub_group))
        
        if not valid_links:
            break
            
        for title, href, current_group in valid_links:
            if href.startswith('/'):
                article_url = f"https://community.instructure.com{href}"
            else:
                article_url = href
                
            content = scrape_article(article_url)
            
            # Format output for NotebookLM
            markdown_lines.append(f"# {title}")
            markdown_lines.append(f"**Category**: {category_name}")
            markdown_lines.append(f"**Group**: {current_group}")
            markdown_lines.append(f"**Article Link**: {article_url}")
            markdown_lines.append("")
            if content:
                markdown_lines.append(content)
            else:
                markdown_lines.append("> *No content available for this article.*")
            markdown_lines.append("")
            markdown_lines.append("---\n")
            
            articles_scraped += 1
            time.sleep(0.5) # Be nice to the server
            
        page += 1

    if articles_scraped == 0:
        return "Error: No articles could be extracted. The URL might be incorrect or access is blocked."

    # Update item count in the envelope via a crude replace since we constructed it line by line
    final_md = "\n".join(markdown_lines)
    
    # Prepend notes
    notes = f"**Notes:**\n- Extracted {articles_scraped} articles from {page-1} page(s)\n- Normalized spacing for readability\n"
    final_md += f"\n{notes}"
    
    return final_md
