import time
import re
from bs4 import BeautifulSoup, Tag, NavigableString
from urllib.parse import urljoin, urlparse
import logging

logger = logging.getLogger(__name__)

def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

class IsamsDeveloperScraper:
    def __init__(self, driver):
        self.driver = driver
        self.seen_urls = set()

    def scrape_article(self, url):
        try:
            self.driver.get(url)
            # Wait for content to appear (ReadMe.io specific)
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # ReadMe pages sometimes take a while to render the .rm-Article content
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, ".rm-Article"))
                )
                # Wait a bit more for internal elements like code blocks and callouts
                time.sleep(2)
            except:
                logger.warning(f"Timeout waiting for .rm-Article on {url}")
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract Breadcrumbs
            breadcrumbs = [a.get_text(strip=True) for a in soup.select(".rm-Breadcrumbs a")]
            
            # Extract Title - priority to the one inside .rm-Article
            title_el = soup.select_one('.rm-Article h1') or soup.find('h1') or soup.select_one('.rm-TitleSection h1')
            title = title_el.get_text(strip=True) if title_el else "Untitled"
            
            # Extract Content Container
            content_div = soup.select_one(".rm-Article")
            if not content_div:
                content_div = soup.select_one("article") or soup.select_one("#content")
            
            content_md = ""
            if content_div:
                content_md = self.process_element_to_markdown(content_div)
            
            if not content_md.strip():
                # Try a broader selector if specifically .rm-Article failed
                content_div = soup.select_one(".rm-Content") or soup.select_one(".markdown-body")
                if content_div:
                    content_md = self.process_element_to_markdown(content_div)

            return {
                "title": title,
                "url": url,
                "breadcrumbs": breadcrumbs,
                "content": content_md
            }
        except Exception as e:
            logger.error(f"Error scraping article {url}: {e}")
            return None

    def process_element_to_markdown(self, element):
        md = ""
        # We want to be careful: finding all tags recursively might return 
        # many parent containers (divs) that wrap the actual content.
        # If we mark a parent div as 'seen', we skip all its children.
        
        # Strategy: 
        # 1. Target semantic content tags directly.
        # 2. Only target 'div' if it is a specialized block (Callout, CodeBlock).
        
        content_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'pre', 'blockquote']
        blocks = element.find_all(content_tags, recursive=True)
        
        # Also find specialized divs
        special_divs = element.find_all('div', class_=lambda c: c and any(cls in c for cls in ['rm-Callout', 'callout', 'rm-CodeBlock', 'highlight']))
        
        # Combine and sort by position in document to preserve order
        all_blocks = blocks + special_divs
        
        # Helper to get sort key (sourceline is best if available, otherwise index in children)
        # Note: sourceline might not be present if the HTML was modified or depending on the BS4 parser used
        def get_sort_key(el):
            return el.sourceline or 0

        # Since sourceline can be unreliable, we can use a custom index if needed
        # But usually in ReadMe docs, they appear in order in find_all
        # Let's use a simpler approach: iterate all children of .rm-Article recursively 
        # but only process the ones that match our criteria and aren't inside already processed ones.
        
        seen_elements = set()
        
        # Re-fetch all potential blocks to ensure we have them in DOM order
        # We include tags that we want to extract content from
        potential_blocks = element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'pre', 'blockquote', 'div'], recursive=True)
        
        i = 0
        while i < len(potential_blocks):
            block = potential_blocks[i]
            if block in seen_elements:
                i += 1
                continue
            
            classes = block.get('class', [])
            # Skip noise
            if any(c in classes for c in ['rm-Article-meta', 'rm-Sidebar', 'rm-Callout-icon', 'rm-Article-navigation', 'rm-Breadcrumbs']):
                i += 1
                continue

            # Check if it's a specialized DIV
            is_special_div = block.name == 'div' and any(c in classes for c in ['rm-Callout', 'callout', 'rm-CodeBlock', 'rm-CodeTabs', 'highlight'])
            
            # If it's a generic div and not a content tag, skip it BUT DON'T MARK CHILDREN AS SEEN
            if block.name == 'div' and not is_special_div:
                i += 1
                continue
            
            text = block.get_text().strip()
            
            # Special Handling for Callouts
            if is_special_div and any(c in classes for c in ['rm-Callout', 'callout']):
                title_el = block.select_one('.rm-Callout-title') or block.select_one('.callout-heading')
                body_el = block.select_one('.rm-Callout-body') or block.select_one('.callout-body')
                title = title_el.get_text(strip=True) if title_el else "Note"
                body = body_el.get_text(strip=True) if body_el else block.get_text().replace(title, '').strip()
                md += f"> **{title}**\n> {body}\n\n"
                
                self.mark_seen_recursive(block, seen_elements)
                i += 1
                continue

            # Special Handling for Prompt/Output
            if block.name in ['p', 'div', 'strong', 'em', 'span'] and re.match(r'^(Prompt|Output):?$', text, re.IGNORECASE):
                label_type = text.replace(':', '').capitalize()
                code_block = self.find_next_code_block(i, potential_blocks)
                
                if code_block:
                    code_el = code_block.find('code')
                    code_text = code_el.get_text().strip() if code_el else code_block.get_text().strip()
                    if '\n' not in code_text and len(code_text) < 150:
                        md += f"**{label_type}**: `{code_text}`\n\n"
                    else:
                        md += f"**{label_type}**:\n```\n{code_text}\n```\n\n"
                    
                    seen_elements.add(block)
                    self.mark_seen_recursive(code_block, seen_elements)
                    i += 1
                    continue

            # Process standard content tags
            if block.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'pre', 'blockquote'] or \
               (block.name == 'div' and 'rm-CodeBlock' in classes):
                
                tag = block.name
                if not text and tag != 'pre':
                    i += 1
                    continue

                if tag.startswith('h'):
                    level = int(tag[1])
                    md += f"{'#' * level} {text}\n\n"
                elif tag == 'p':
                    md += f"{text}\n\n"
                elif tag == 'ul':
                    for li in block.find_all('li', recursive=False):
                        md += f"- {li.get_text(strip=True)}\n"
                    md += "\n"
                elif tag == 'ol':
                    for k, li in enumerate(block.find_all('li', recursive=False)):
                        md += f"{k+1}. {li.get_text(strip=True)}\n"
                    md += "\n"
                elif tag == 'pre' or 'rm-CodeBlock' in classes or 'highlight' in classes:
                    code_el = block.find('code')
                    code_text = code_el.get_text().strip() if code_el else block.get_text().strip()
                    md += f"```\n{code_text}\n```\n\n"
                elif tag == 'blockquote':
                    md += f"> {text}\n\n"
                
                self.mark_seen_recursive(block, seen_elements)

            i += 1
        return md

    def mark_seen_recursive(self, element, seen_set):
        seen_set.add(element)
        for child in element.find_all(True):
            seen_set.add(child)

    def find_next_code_block(self, current_index, blocks):
        for j in range(current_index + 1, min(current_index + 10, len(blocks))):
            b = blocks[j]
            classes = b.get('class', [])
            if b.name == 'pre' or any(c in classes for c in ['rm-CodeBlock', 'highlight']):
                return b
        return None

    def discover_links(self, base_url):
        links = []
        try:
            # The sidebar links have class .rm-Sidebar-link
            sidebar = BeautifulSoup(self.driver.page_source, 'html.parser').select_one('#hub-sidebar')
            if sidebar:
                for a in sidebar.find_all('a', href=True, class_='rm-Sidebar-link'):
                    href = a['href']
                    full_url = urljoin(base_url, href).split('#')[0]
                    if full_url not in links and full_url != base_url:
                        # Heuristic: only stay within developer docs
                        if 'developer.isams.com' in full_url:
                            links.append(full_url)
        except Exception as e:
            logger.error(f"Error discovering links: {e}")
        return links

def scrape_isams_developer(url, driver):
    scraper = IsamsDeveloperScraper(driver)
    
    # Scrape main article
    main_article = scraper.scrape_article(url)
    if not main_article:
        return "Failed to scrape main article."
    
    # Discover and scrape sub-articles
    sub_links = scraper.discover_links(url)
    all_articles = [main_article]
    
    # We want to be careful not to scrape the whole site if it's too big
    # But for a specific section like /docs/batch-api, it should be manageable
    # We'll filter links to make sure they are sub-paths if possible
    base_path = urlparse(url).path
    for sub_url in sub_links:
        if urlparse(sub_url).path.startswith(base_path) and sub_url != url:
            article = scraper.scrape_article(sub_url)
            if article:
                all_articles.append(article)
    
    # Format into single Markdown
    final_md = ""
    for art in all_articles:
        final_md += f"# {art['title']}\n"
        final_md += f"**Link**: {art['url']}\n"
        if art['breadcrumbs']:
            final_md += f"**Path**: {' > '.join(art['breadcrumbs'])}\n"
        final_md += f"\n{art['content']}\n"
        final_md += "---\n\n"
        
    return final_md
