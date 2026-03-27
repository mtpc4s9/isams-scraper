import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import logging
import re
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from markdownify import markdownify as md_converter

logger = logging.getLogger(__name__)

def clean_text(text):
    if not text: return ""
    return re.sub(r'\s+', ' ', text).strip()

def strip_markdown_links(md_text):
    """
    Converts [Link Text](url) to just Link Text.
    Handles nested parentheses in titles like [Text (with parens)](url "Title (with parens)")
    """
    # Pattern: [text](url "title") or [text](url)
    # Using a more robust non-greedy approach for the parenthetical part
    return re.sub(r'\[([^\]]+)\]\((?:[^)(]+|\([^)(]*\))*\)', r'\1', md_text)

def extract_category_1(url):
    try:
        parsed = urlparse(url)
        parts = parsed.path.strip('/').split('/')
        if parts:
            return parts[0] # e.g., pssis-admin
    except Exception:
        pass
    return "Unknown"

def scrape_powerschool_article(driver, url, role_name, category_1, category_2, article_name):
    driver.get(url)
    time.sleep(2) # adjust wait if needed
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Try multiple common doc content selectors
    main_content = soup.find('main') or soup.find('div', class_='doc-body') or soup.find('article')
    
    content_md = ""
    if main_content:
        # Use markdownify for a much cleaner, flow-based conversion
        content_md = md_converter(
            str(main_content),
            heading_style="ATX",
            newline_style="MD", # Ensure consistent line breaks
            strip=['script', 'style', 'nav', 'aside', 'footer', 'header']
        ).strip()

        # Heuristic for "Agenda" pages: if the content is mostly links, strip the link syntax
        # We check the ratio of link syntax vs total length
        link_syntax_count = content_md.count('](')
        if link_syntax_count > 0:
            total_lines = content_md.count('\n') + 1
            # If average links per line is > 0.3, or many links overall with short total text
            if link_syntax_count / total_lines > 0.3 or link_syntax_count > 5:
                logger.info(f"Detected potential Agenda page at {url} (Links: {link_syntax_count}, Lines: {total_lines}). Stripping links for pure text.")
                content_md = strip_markdown_links(content_md)
    else:
        content_md = "No main content found for this article."

    md = "---\n"
    md += f"Article name: {article_name}\n"
    md += f"Article link: {url}\n"
    md += f"Role: {role_name}\n"
    md += f"Category 1: {category_1}\n"
    md += f"Category 2: {category_2}\n"
    md += "---\n\n"
    md += content_md
    md += "\n---\n\n"
    return md

def scrape_powerschool(url: str, role: str, driver):
    """
    Main entrypoint for PowerSchool Docs Scraper.
    Uses Selenium to parse the left sidebar, get all links, and scrape them.
    """
    logger.info(f"Starting PowerSchool Scrape for: {url}")
    
    driver.get(url)
    
    # Wait for the sidebar to load. We will use a generic wait for 'nav' or common sidebar classes
    logger.info("Waiting for sidebar elements to appear...")
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".vp-desktop-navigation__page-tree, .vp-tree__container, nav, .sidebar, aside, .vp-sidebar"))
        )
        logger.info("Sidebar elements detected.")
    except Exception as e:
        logger.warning(f"Timeout waiting for sidebar: {str(e)}. Will proceed with current source.")
        
    time.sleep(5) # Extra wait for JS rendering
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    category_1_slug = extract_category_1(url)
    
    # Try to get a nicer category name from the title or meta
    category_1 = soup.title.string.split('|')[0].strip() if soup.title else category_1_slug
    # Fallback: if title is too generic like "Support and Resources", use slug but capitalized
    if len(category_1) > 50 or "Support" in category_1:
        category_1 = category_1_slug.replace('-', ' ').title()
    
    # Find the sidebar navigation
    sidebar = soup.select_one('.vp-desktop-navigation__page-tree, .vp-tree__container, .md-sidebar--primary, .sidebar, [role="navigation"], aside, nav.vp-sidebar, .vp-sidebar, nav')
    if not sidebar:
        sidebar = soup # Fallback to whole page if no obvious sidebar
        
    # Heuristic to find Father and Son links
    # Often, documentation sidebars have lists (ul/li) where a grouping li has a span/button for Father and a nested ul with a for Sons.
    # Or we can just look at all <a> tags and find their closest preceding header.
    
    links_to_scrape = [] # List of dict: {url, father, child}
    
    # Let's try to find all links in the sidebar
    a_tags = sidebar.find_all('a', href=True)
    seen_urls = set()
    
    # If the user provides a specific start URL, we should ensure we only scrape links on the same host and ideally same base path
    parsed_base = urlparse(url)
    base_domain = f"{parsed_base.scheme}://{parsed_base.netloc}"
    
    for a in a_tags:
        href = a['href']
        full_url = urljoin(url, href)
        
        # Make sure it's a doc link and same category
        if full_url in seen_urls: continue
        if not full_url.startswith(base_domain): continue
        if category_1_slug not in full_url: continue # keep it in the same category zone
        if "#" in full_url:
            full_url = full_url.split('#')[0] # Remove anchors
            if full_url in seen_urls: continue
            
        seen_urls.add(full_url)
        
        # Son name is just link text
        son_name = clean_text(a.get_text())
        if not son_name: continue
        
        # Father name extraction heuristic:
        # Traverse up the DOM to find all parent titles in the tree
        parent_titles = []
        curr = a.parent
        while curr and curr != sidebar:
            # Look for elements that usually contain titles of sections in the tree
            # Many docs use .vp-tree-item__header__title for the grouping name
            title_elem = curr.select_one('.vp-tree-item__header__title, .vp-tree-item__header, span, b, strong')
            if title_elem:
                title_text = clean_text(title_elem.get_text())
                if title_text and title_text != son_name and title_text not in parent_titles:
                    parent_titles.insert(0, title_text)
            curr = curr.parent
            
        father_name = " > ".join(parent_titles) if parent_titles else "General"

        links_to_scrape.append({
            'url': full_url,
            'father': father_name,
            'son': son_name,
            'slug': category_1_slug
        })

    logger.info(f"Found {len(links_to_scrape)} links to scrape.")
    
    if len(links_to_scrape) == 0:
        # Debug: Save page source to see why it failed
        try:
            with open("backend/article_error.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            logger.error(f"No links found. Saved page source to backend/article_error.html for debugging. URL: {url}")
        except:
            pass
        return "Error: Could not find any navigation links on this page. The page structure might have changed or rendering failed."

    final_markdown = f"# PowerSchool Documentation Scrape\n**Category 1**: {category_1}\n**Role**: {role}\n\n"
    
    # Optional: Limiting to first 5 for sanity check if too many? No, user wants all.
    # We will scrape them sequentially.
    for item in links_to_scrape:
        md = scrape_powerschool_article(driver, item['url'], role, item.get('slug', category_1_slug), item['father'], item['son'])
        final_markdown += md
        
    return final_markdown
