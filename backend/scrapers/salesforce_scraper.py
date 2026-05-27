import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

def clean_text(text):
    if not text:
        return ""
    # Normalize multiple whitespaces and newlines
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def scrape_single_page(url: str, soup: BeautifulSoup, module_name: str = "") -> str:
    """
    Scrapes a single Salesforce page and extracts clean content as Markdown.
    Supports Page Builder, WordPress Blog, and AEM templates.
    """
    # 1. Extract Article Name from H1 inside marquee, blog header, any H1, or title fallback
    article_name = ""
    h1 = soup.find('h1', class_=re.compile("headline|marquee__headline|post__title"))
    if not h1:
        h1 = soup.find('h1')
    if h1:
        article_name = clean_text(h1.get_text())
    else:
        # Fallback to title
        title_tag = soup.find('title')
        if title_tag:
            article_name = clean_text(title_tag.get_text().split('|')[0])
        else:
            article_name = "Untitled Salesforce Article"
            
    content_blocks = []
    
    # Identify containers for different Salesforce templates
    blades = soup.find_all(['section', 'div'], class_=re.compile(r'marquee--blade|textmainbody--blade|nup--blade'))
    blog_containers = soup.find_all(['div', 'article'], class_=re.compile(r'post__content|post__content-v2'))
    aem_elements = soup.find_all(['div', 'section'], class_=re.compile(r'bodyCopyComponent|headingComponent|headingLargeComponent|headingSmallLightComponent'))
    
    # 2. Template Cascade Execution
    if blades:
        # Case A: Page Builder Template
        for blade in blades:
            classes = blade.get('class', [])
            is_marquee = any('marquee--blade' in cls for cls in classes)
            
            if is_marquee:
                desc = blade.find(class_=re.compile("description|headline--standard"))
                if desc:
                    txt = clean_text(desc.get_text())
                    if txt and txt not in content_blocks:
                        content_blocks.append(f"{txt}\n\n")
                continue
                
            for child in blade.find_all(['h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'table'], recursive=True):
                # Skip elements inside list items to avoid duplication
                if child.find_parent('li'):
                    continue
                tag_name = child.name
                
                if tag_name in ['h2', 'h3', 'h4', 'h5', 'h6']:
                    level = int(tag_name[1])
                    hashes = "#" * level
                    txt = clean_text(child.get_text())
                    if txt:
                        content_blocks.append(f"{hashes} {txt}\n\n")
                elif tag_name == 'p':
                    txt = clean_text(child.get_text())
                    if txt:
                        content_blocks.append(f"{txt}\n\n")
                elif tag_name == 'ul':
                    list_items = []
                    for li in child.find_all('li', recursive=False):
                        txt = clean_text(li.get_text())
                        if txt:
                            list_items.append(f"- {txt}")
                    if list_items:
                        content_blocks.append("\n".join(list_items) + "\n\n")
                elif tag_name == 'ol':
                    list_items = []
                    for idx, li in enumerate(child.find_all('li', recursive=False)):
                        txt = clean_text(li.get_text())
                        if txt:
                            list_items.append(f"{idx+1}. {txt}")
                    if list_items:
                        content_blocks.append("\n".join(list_items) + "\n\n")
                elif tag_name == 'table':
                    rows = []
                    for tr in child.find_all('tr'):
                        cells = [clean_text(td.get_text()) for td in tr.find_all(['td', 'th'])]
                        if any(cells):
                            rows.append(" | ".join(cells))
                    if rows:
                        content_blocks.append("\n".join(rows) + "\n\n")
                        
    elif blog_containers:
        # Case B: WordPress Blog Template
        container = blog_containers[0]
        for tag in container.find_all(class_=re.compile("post__social|subscribe|byline|author")):
            tag.decompose()
            
        for child in container.find_all(['h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'table'], recursive=True):
            if child.find_parent('li'):
                continue
            tag_name = child.name
            
            if tag_name in ['h2', 'h3', 'h4', 'h5', 'h6']:
                level = int(tag_name[1])
                hashes = "#" * level
                txt = clean_text(child.get_text())
                if txt:
                    content_blocks.append(f"{hashes} {txt}\n\n")
            elif tag_name == 'p':
                txt = clean_text(child.get_text())
                if txt:
                    content_blocks.append(f"{txt}\n\n")
            elif tag_name == 'ul':
                list_items = []
                for li in child.find_all('li', recursive=False):
                    txt = clean_text(li.get_text())
                    if txt:
                        list_items.append(f"- {txt}")
                if list_items:
                    content_blocks.append("\n".join(list_items) + "\n\n")
            elif tag_name == 'ol':
                list_items = []
                for idx, li in enumerate(child.find_all('li', recursive=False)):
                    txt = clean_text(li.get_text())
                    if txt:
                        list_items.append(f"{idx+1}. {txt}")
                if list_items:
                    content_blocks.append("\n".join(list_items) + "\n\n")
            elif tag_name == 'table':
                rows = []
                for tr in child.find_all('tr'):
                    cells = [clean_text(td.get_text()) for td in tr.find_all(['td', 'th'])]
                    if any(cells):
                        rows.append(" | ".join(cells))
                if rows:
                    content_blocks.append("\n".join(rows) + "\n\n")
                    
    elif aem_elements:
        # Case C: Adobe Experience Manager (AEM) Template
        for el in aem_elements:
            classes = el.get('class', [])
            is_heading = any('headingComponent' in cls or 'headingLargeComponent' in cls or 'headingSmallLightComponent' in cls for cls in classes)
            
            if is_heading:
                h_tag = el.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                txt = clean_text(el.get_text())
                if txt:
                    if txt == article_name:
                        continue
                    if h_tag:
                        level = int(h_tag.name[1])
                        hashes = "#" * level
                        content_blocks.append(f"{hashes} {txt}\n\n")
                    else:
                        content_blocks.append(f"## {txt}\n\n")
            else:
                # It is a bodyCopyComponent
                children = el.find_all(['p', 'ul', 'ol', 'table'], recursive=False)
                if not children:
                    txt = clean_text(el.get_text())
                    if txt:
                        content_blocks.append(f"{txt}\n\n")
                else:
                    for child in el.find_all(['p', 'ul', 'ol', 'table'], recursive=True):
                        if child.find_parent('li'):
                            continue
                        tag_name = child.name
                        if tag_name == 'p':
                            txt = clean_text(child.get_text())
                            if txt:
                                content_blocks.append(f"{txt}\n\n")
                        elif tag_name == 'ul':
                            list_items = []
                            for li in child.find_all('li', recursive=False):
                                txt = clean_text(li.get_text())
                                if txt:
                                    list_items.append(f"- {txt}")
                            if list_items:
                                content_blocks.append("\n".join(list_items) + "\n\n")
                        elif tag_name == 'ol':
                            list_items = []
                            for idx, li in enumerate(child.find_all('li', recursive=False)):
                                txt = clean_text(li.get_text())
                                if txt:
                                    list_items.append(f"{idx+1}. {txt}")
                            if list_items:
                                content_blocks.append("\n".join(list_items) + "\n\n")
                        elif tag_name == 'table':
                            rows = []
                            for tr in child.find_all('tr'):
                                cells = [clean_text(td.get_text()) for td in tr.find_all(['td', 'th'])]
                                if any(cells):
                                    rows.append(" | ".join(cells))
                            if rows:
                                content_blocks.append("\n".join(rows) + "\n\n")

    # Combine and de-duplicate adjacent blocks
    clean_blocks = []
    for block in content_blocks:
        if not clean_blocks or clean_blocks[-1] != block:
            clean_blocks.append(block)
            
    content_text = "".join(clean_blocks).strip()
    content_text = content_text.replace("(Back to top)", "").strip()
    
    if not content_text:
        return ""
    
    # 3. Format complete NotebookLM Source Markdown
    md_out = []
    md_out.append(f"# {article_name}")
    md_out.append(f"**Module**: {module_name}")
    md_out.append(f"**Article Link**: {url}")
    md_out.append("\n---\n")
    md_out.append(content_text)
    
    return "\n".join(md_out)

def scrape_salesforce(url: str, module_name: str = "") -> str:
    """
    Hierarchical Cascading Scraper for Salesforce Articles.
    Supports scraping a single page or automatically crawling nested sub-pages
    detected in the left panel navigation menu.
    
    Args:
        url (str): The Salesforce public doc/category URL.
        module_name (str): The classification module input by the user.
        
    Returns:
        str: The extracted content formatted as clean Markdown, ready for NotebookLM.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        return f"Error: Failed to fetch the URL. details: {str(e)}"
        
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 1. Scrape the parent page first
    parent_md = scrape_single_page(url, soup, module_name)
    
    # 2. Try to detect child navigation links inside sidebar menu (under li.active > ul.page-list)
    child_urls = []
    page_list_menu = soup.find('ul', class_=re.compile("page-list"))
    if page_list_menu:
        active_li = page_list_menu.find('li', class_=re.compile("active"))
        if active_li:
            nested_ul = active_li.find('ul', class_=re.compile("page-list"))
            if nested_ul:
                # Found nested child list! Extract all links inside it
                links = nested_ul.find_all('a', href=True)
                for l in links:
                    full_url = urljoin(url, l['href'])
                    # Normalize to remove query/anchor tags
                    full_url_clean = full_url.split('?')[0].split('#')[0]
                    parent_url_clean = url.split('?')[0].split('#')[0]
                    if full_url_clean != parent_url_clean and full_url_clean not in child_urls:
                        child_urls.append(full_url_clean)
                        
    # 3. Perform recursive crawing for each sub-page (max 15 to avoid timeouts)
    all_md_parts = []
    if parent_md:
        all_md_parts.append(parent_md)
        
    scraped_count = 0
    for child in child_urls[:15]:
        try:
            res = requests.get(child, headers=headers)
            # Skip page if it redirects to 404 or fails
            if res.status_code != 200:
                continue
            child_soup = BeautifulSoup(res.content, 'html.parser')
            child_md = scrape_single_page(child, child_soup, module_name)
            if child_md:
                all_md_parts.append(child_md)
                scraped_count += 1
        except Exception:
            # Silently pass to keep output clean and skip failed items
            continue
            
    final_output = "\n\n---\n\n".join(all_md_parts)
    
    if not final_output:
        return f"Error: No content extracted. Please verify if the URL is a public Salesforce Article or Category page. URL: {url}"
        
    return final_output
