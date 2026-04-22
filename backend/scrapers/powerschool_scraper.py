import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import logging
import re
import requests
import threading
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from markdownify import markdownify as md_converter

logger = logging.getLogger(__name__)
driver_lock = threading.Lock()

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

def extract_links_from_pagetree(nodes, base_domain, category_1_slug, parent_title="General"):
    links = []
    for node in nodes:
        title = node.get("title", "")
        path = node.get("path", "")
        
        if path:
            full_url = urljoin(base_domain, path)
            links.append({
                'url': full_url,
                'father': parent_title,
                'son': title,
                'slug': category_1_slug
            })
            
        children = node.get("children", [])
        if children:
            new_father = f"{parent_title} > {title}" if parent_title and parent_title != "General" else title
            links.extend(extract_links_from_pagetree(children, base_domain, category_1_slug, new_father))
            
    return links

def scrape_powerschool_article(driver, url, role_name, category_1, category_2, article_name):
    logger.info(f"Scraping article: {article_name} ({url})")
    try:
        # Strategy A: Fast static fetch (WebFetch approach)
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
        else:
            raise Exception(f"HTTP {response.status_code}")
    except Exception as e:
        # Strategy B: Fallback to Browser automation
        logger.warning(f"WebFetch failed for {url} ({e}), falling back to Selenium...")
        with driver_lock:
            driver.get(url)
            time.sleep(2) # adjust wait if needed
            soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Try multiple common doc content selectors
    main_content = soup.find('main') or soup.find('div', class_='doc-body') or soup.find('article')
    
    content_md = ""
    if main_content:
        # Clean up unwanted tags (remove them and their content completely)
        for tag in main_content.find_all(['script', 'style', 'noscript', 'nav', 'aside', 'footer', 'header']):
            tag.decompose()

        # Use markdownify for a much cleaner, flow-based conversion
        content_md = md_converter(
            str(main_content),
            heading_style="ATX",
            newline_style="MD", # Ensure consistent line breaks
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
    
    category_1_slug = extract_category_1(url)
    
    # Try to get a nicer category name from the title or meta
    # We load the page first just to get the title
    driver.get(url)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    category_1 = soup.title.string.split('|')[0].strip() if soup.title else category_1_slug
    if len(category_1) > 50 or "Support" in category_1:
        category_1 = category_1_slug.replace('-', ' ').title()

    links_to_scrape = []
    
    # Attempt to fetch __pagetree.json for full recursive hierarchy
    parsed_base = urlparse(url)
    base_domain = f"{parsed_base.scheme}://{parsed_base.netloc}"
    parts = parsed_base.path.strip('/').split('/')
    
    pagetree_data = None
    for i in range(len(parts), 0, -1):
        prefix = "/".join(parts[:i])
        pagetree_url = f"{base_domain}/{prefix}/__pagetree.json"
        logger.info(f"Attempting to fetch full page tree from {pagetree_url}")
        try:
            response = requests.get(pagetree_url, timeout=5)
            if response.status_code == 200:
                pagetree_data = response.json()
                logger.info(f"Successfully found __pagetree.json at {pagetree_url}")
                break
        except Exception as e:
            logger.debug(f"Failed to fetch {pagetree_url}: {e}")

    if pagetree_data:
        tree_nodes = pagetree_data if isinstance(pagetree_data, list) else pagetree_data.get("value", [])
        links_to_scrape = extract_links_from_pagetree(tree_nodes, base_domain, category_1_slug)
        logger.info(f"Successfully retrieved {len(links_to_scrape)} links from __pagetree.json")
    else:
        logger.warning(f"Failed to find __pagetree.json for any path prefix.")

    # Fallback to scraping the sidebar if __pagetree.json failed
    if not links_to_scrape:
        logger.info("Falling back to scraping the sidebar from DOM...")
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".vp-desktop-navigation__page-tree, .vp-tree__container, nav, .sidebar, aside, .vp-sidebar"))
            )
            logger.info("Sidebar elements detected.")
        except Exception as e:
            logger.warning(f"Timeout waiting for sidebar: {str(e)}. Will proceed with current source.")
            
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        sidebar = soup.select_one('.vp-desktop-navigation__page-tree, .vp-tree__container, .md-sidebar--primary, .sidebar, [role="navigation"], aside, nav.vp-sidebar, .vp-sidebar, nav')
        if not sidebar:
            sidebar = soup 
            
        a_tags = sidebar.find_all('a', href=True)
        seen_urls = set()
        
        for a in a_tags:
            href = a['href']
            full_url = urljoin(url, href)
            
            if full_url in seen_urls: continue
            if not full_url.startswith(base_domain): continue
            if category_1_slug not in full_url: continue 
            if "#" in full_url:
                full_url = full_url.split('#')[0] 
                if full_url in seen_urls: continue
                
            seen_urls.add(full_url)
            
            son_name = clean_text(a.get_text())
            if not son_name: continue
            
            parent_titles = []
            curr = a.parent
            while curr and curr != sidebar:
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
    # We will scrape them concurrently to prevent timeouts on large sites like Schoology
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    def fetch_article(item):
        return scrape_powerschool_article(driver, item['url'], role, item.get('slug', category_1_slug), item['father'], item['son'])

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_article, item) for item in links_to_scrape]
        for future in as_completed(futures):
            try:
                final_markdown += future.result()
            except Exception as e:
                logger.error(f"Error scraping article: {e}")
        
    return final_markdown
