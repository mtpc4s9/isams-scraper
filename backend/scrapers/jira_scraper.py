import time
import re
import requests
import logging
from bs4 import BeautifulSoup
import markdownify
from urllib.parse import urljoin
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def parse_article_content(html_content: str, url: str, topic: str, article_name: str) -> str:
    """Parses Atlassian Support article HTML and converts it to clean Markdown."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Atlassian article main body container selectors - prioritizing high-fidelity wrappers
    content_div = None
    selectors = [
        'div.topic__body',
        'div.ak-renderer-document',
        'div.support-content', 
        'div.kb-article-body',
        'div#help-content-container', 
        'article', 
        'div.page-content',
        'main',
        'div.content'
    ]
    for sel in selectors:
        content_div = soup.select_one(sel)
        if content_div:
            break
            
    if not content_div:
        content_div = soup.find('body')
        
    if not content_div:
        return f"## {article_name}\n**Topic**: {topic}\n**Article Link**: {url}\n\n*Error: Could not extract content.*\n\n---\n\n"
        
    # Decompose unwanted elements safely to avoid cluttering NotebookLM
    unwanted_selectors = [
        'script', 'style', 'nav', 'header', 'footer', 
        '.feedback-container', '.breadcrumbs', '.sidebar', 
        '.related-articles', '.show-more-btn', '.additional-help', 
        '.feedback-panel', '.was-this-helpful', '#still-need-help'
    ]
    for unwanted in content_div.select(', '.join(unwanted_selectors)):
        unwanted.decompose()

    # Decompose "Still need help?" and subsequent widgets if they are at the end
    for heading in content_div.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        h_text = heading.get_text().lower()
        if "still need help" in h_text or "need help?" in h_text:
            siblings_to_decompose = []
            curr = heading
            while curr:
                siblings_to_decompose.append(curr)
                curr = curr.next_sibling
            for sib in siblings_to_decompose:
                if hasattr(sib, 'decompose'):
                    sib.decompose()
            break
        
    # Convert to markdown
    text_content = markdownify.markdownify(
        str(content_div),
        heading_style="ATX",
        escape_underscores=False,
        escape_asterisks=False
    ).strip()

    # Post-conversion Regex sanitization to fully strip any residual feedback widget text
    text_content = re.sub(
        r'Was this helpful\?\s*Yes\s*No\s*(?:It wasn\'t accurate)?(?:It wasn\'t clear)?(?:It wasn\'t relevant)?\s*(?:Provide feedback about this article)?', 
        '', 
        text_content, 
        flags=re.IGNORECASE
    )
    
    text_content = re.sub(
        r'#*\s*Still need help\?.*?(?:\[Ask the Community\].*?\))?', 
        '', 
        text_content, 
        flags=re.IGNORECASE | re.DOTALL
    )

    # Normalize double newlines and clean endings
    text_content = re.sub(r'\n{3,}', '\n\n', text_content).strip()
    
    # Build cleanly formatted markdown block
    md_block = (
        f"## {article_name}\n"
        f"**Topic**: {topic}\n"
        f"**Article Link**: {url}\n\n"
        f"{text_content}\n"
        f"\n---\n\n"
    )
    return md_block

def extract_sub_articles(html_content: str, base_url: str):
    """
    Detects if a support page is a hub page containing sub-topic cards or links to sub-articles.
    Returns a list of tuples (article_name, article_url) if detected, otherwise empty list.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    sub_articles = []
    
    # 1. Search for card containers: li[data-testid="card-item"], article, or card class
    card_items = soup.select('li[data-testid="card-item"], article, div.card, div.topic-card')
    for card in card_items:
        a_tag = card.find('a', href=True)
        if a_tag:
            full_href = urljoin(base_url, a_tag['href'])
            # Basic validation
            if 'support.atlassian.com' in full_href and full_href.split('?')[0].split('#')[0] != base_url.split('?')[0].split('#')[0]:
                # Headings only to avoid parent-div long text concat bugs
                h_tag = card.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                if not h_tag:
                    h_tag = card.select_one('[class*="heading"], [class*="title"]')
                
                name = clean_text(h_tag.get_text()) if h_tag else clean_text(a_tag.get_text())
                if name.lower() in ["view topic", "view article", "learn more", "read more"]:
                    name = clean_text(a_tag.get_text())
                if not name or len(name) < 2:
                    name = "Sub-Article"
                sub_articles.append((name, full_href))
                
    # 2. Search for any standard links containing "View topic" text
    for a in soup.find_all('a', href=True):
        a_text = clean_text(a.get_text()).lower()
        if "view topic" in a_text or "view article" in a_text:
            full_href = urljoin(base_url, a['href'])
            if 'support.atlassian.com' in full_href and full_href.split('?')[0].split('#')[0] != base_url.split('?')[0].split('#')[0]:
                name = ""
                parent_card = a.find_parent(['li', 'div', 'article'])
                if parent_card:
                    h_tag = parent_card.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                    if h_tag:
                        name = clean_text(h_tag.get_text())
                if not name:
                    name = clean_text(a.get_text())
                
                if full_href not in [sa[1] for sa in sub_articles]:
                    sub_articles.append((name, full_href))
                    
    # Remove duplicate urls
    unique_subs = []
    seen = set()
    for name, href in sub_articles:
        clean_url = href.split('?')[0].split('#')[0]
        if clean_url not in seen:
            seen.add(clean_url)
            unique_subs.append((name, href))
            
    return unique_subs

def scrape_jira(url: str, topic: str, driver, headless: bool = True) -> str:
    """
    Scrapes guidelines for JIRA on Scrum from Atlassian Support.
    
    Args:
        url (str): Target URL (https://support.atlassian.com/jira-software-cloud/resources/)
        topic (str): The specific topic to scrape (fuzzy matched against <h3> topic title).
        driver: Selenium webdriver.
        headless (bool): Headless mode toggle.
        
    Returns:
        str: Comprehensive combined Markdown file ready for Google NotebookLM.
    """
    logger.info(f"Navigating to: {url}")
    driver.get(url)
    time.sleep(5) # Allow dynamic content to render
    
    # 1. Find all H3 elements on page
    h3_elements = driver.find_elements(By.CSS_SELECTOR, "h3.ternary-heading, h3")
    matched_h3 = None
    matched_text = ""
    
    logger.info(f"Found {len(h3_elements)} heading candidates.")
    
    # Fuzzy match the topic
    topic_cleaned = clean_text(topic).lower()
    for h3 in h3_elements:
        h3_text = clean_text(h3.text)
        if topic_cleaned in h3_text.lower():
            matched_h3 = h3
            matched_text = h3_text
            logger.info(f"Successfully matched topic: '{h3_text}' for user query: '{topic}'")
            break
            
    if not matched_h3:
        # Fallback: List available topics to help the user
        available_topics = [clean_text(h.text) for h in h3_elements if clean_text(h.text)]
        return f"Error: Could not find any topic matching '{topic}'. Available topics are:\n" + "\n".join([f"- {t}" for t in available_topics[:15]])
        
    # 2. Find the container and Click 'Show more' button if present
    parent_container = matched_h3
    button = None
    
    # Traverse up to 4 levels to locate the button
    for _ in range(4):
        try:
            parent_container = parent_container.find_element(By.XPATH, "..")
            buttons = parent_container.find_elements(By.CSS_SELECTOR, "button[data-testid='show-more-btn'], button.chevron-down")
            if buttons:
                button = buttons[0]
                break
        except Exception:
            break
            
    if button:
        logger.info(f"Found 'Show more' button. Clicking to expand guidelines under section: '{matched_text}'")
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            time.sleep(1)
            try:
                button.click()
            except Exception:
                driver.execute_script("arguments[0].click();", button)
            time.sleep(3) # Wait for expansion transition and data fetching
            logger.info("Successfully clicked 'Show more' button.")
        except Exception as e:
            logger.warning(f"Could not click 'Show more' button: {e}. Attempting extraction anyway.")
    else:
        logger.info(f"No 'Show more' button found for section '{matched_text}' or it's already expanded.")
        
    # 3. Extract all guideline links under this topic section
    links_elements = []
    if parent_container:
        links_elements = parent_container.find_elements(By.CSS_SELECTOR, "a[data-testid='atlas_link'], ul.documentation-collection__child-list a")
        
    if not links_elements:
        logger.info("Falling back to sibling link extraction.")
        collect = False
        for elem in driver.find_elements(By.XPATH, "//*"):
            if elem == matched_h3:
                collect = True
                continue
            if collect and elem.tag_name in ['h1', 'h2', 'h3'] and elem.get_attribute('class') == 'ternary-heading':
                break
            if collect and elem.tag_name == 'a':
                href = elem.get_attribute('href')
                data_testid = elem.get_attribute('data-testid')
                if href and (data_testid == 'atlas_link' or 'support.atlassian.com' in href):
                    links_elements.append(elem)
                    
    # Clean and de-duplicate links
    seen_hrefs = set()
    articles_to_scrape = []
    for l in links_elements:
        try:
            href = l.get_attribute('href')
            name = clean_text(l.text)
            if href and href not in seen_hrefs:
                if 'support.atlassian.com' in href and name:
                    seen_hrefs.add(href)
                    articles_to_scrape.append((name, href))
        except Exception:
            continue
            
    # Remove artificial limit to allow scraping all available articles in a topic
    # articles_to_scrape = articles_to_scrape[:50]
    
    if not articles_to_scrape:
        return f"Error: No guidelines found under the topic '{matched_text}'."
        
    logger.info(f"Found {len(articles_to_scrape)} articles to scrape. Beginning hybrid content extraction...")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    })
    
    # Determine a friendly title prefix based on the Atlassian product in the URL
    product_title = "Atlassian Support"
    if "jira-service-management-cloud" in url:
        product_title = "Jira Service Management"
    elif "jira-software-cloud" in url:
        product_title = "Jira Software"
    elif "confluence-cloud" in url:
        product_title = "Confluence"
    elif "jira" in url:
        product_title = "Jira"

    combined_markdown = (
        f"# {product_title} Guidelines: {matched_text}\n"
        f"**Source Resources**: {url}\n"
        f"**Topic Category (Manual)**: {topic}\n"
        f"**Total Articles Scraped**: {len(articles_to_scrape)}\n\n"
        f"---\n\n"
    )
    
    for idx, (art_name, art_url) in enumerate(articles_to_scrape, 1):
        logger.info(f"[{idx}/{len(articles_to_scrape)}] Scraping parent guideline: {art_name} -> {art_url}")
        html = ""
        success = False
        
        # Strategy A: Requests + BS4
        try:
            res = session.get(art_url, timeout=15)
            if res.status_code == 200:
                html = res.text
                if "support-content" in html or "kb-article-body" in html or "help-content" in html or "h1" in html or "topic__body" in html:
                    success = True
                    logger.info("  -> Successfully fetched parent page via Requests.")
        except Exception as e:
            logger.warning(f"  -> Requests failed for {art_url}: {e}")
            
        # Strategy B: Fallback to Selenium
        if not success:
            logger.info("  -> Falling back to Selenium for parent page...")
            try:
                driver.get(art_url)
                time.sleep(4)
                html = driver.page_source
                success = True
                logger.info("  -> Successfully fetched parent page via Selenium.")
            except Exception as e:
                logger.error(f"  -> Selenium also failed for parent {art_url}: {e}")
                combined_markdown += f"## {art_name}\n**Topic**: {topic}\n**Article Link**: {art_url}\n\n*Error: Failed to fetch article content.*\n\n---\n\n"
                continue
                
        # --- Deep Crawling of Sub-Articles within Card/Landing items ---
        sub_articles = extract_sub_articles(html, art_url)
        
        if sub_articles:
            logger.info(f"  -> Hub page detected! Crawling {len(sub_articles)} sub-articles...")
            for sub_idx, (sub_name, sub_url) in enumerate(sub_articles, 1):
                logger.info(f"    -> Sub-Article [{sub_idx}/{len(sub_articles)}]: {sub_name} -> {sub_url}")
                sub_html = ""
                sub_success = False
                
                # Fetch sub-article via requests
                try:
                    res = session.get(sub_url, timeout=15)
                    if res.status_code == 200:
                        sub_html = res.text
                        if "support-content" in sub_html or "kb-article-body" in sub_html or "help-content" in sub_html or "h1" in sub_html or "topic__body" in sub_html:
                            sub_content = parse_article_content(sub_html, sub_url, topic, sub_name)
                            if sub_content and len(sub_content.strip()) > 200:
                                sub_success = True
                                combined_markdown += sub_content
                                logger.info("      -> Successfully fetched sub-article via Requests.")
                except Exception as e:
                    logger.warning(f"      -> Requests failed for sub-article: {e}")
                    
                # Fetch sub-article via Selenium
                if not sub_success:
                    logger.info("      -> Falling back to Selenium for sub-article...")
                    try:
                        driver.get(sub_url)
                        time.sleep(4)
                        sub_html = driver.page_source
                        sub_content = parse_article_content(sub_html, sub_url, topic, sub_name)
                        combined_markdown += sub_content
                        logger.info("      -> Successfully fetched sub-article via Selenium.")
                    except Exception as e:
                        logger.error(f"      -> Selenium failed for sub-article {sub_url}: {e}")
                        combined_markdown += f"## {sub_name}\n**Topic**: {topic}\n**Article Link**: {sub_url}\n\n*Error: Failed to fetch sub-article content.*\n\n---\n\n"
                
                time.sleep(1) # Polite rate limiting
        else:
            # Standard single article scraping
            art_content = parse_article_content(html, art_url, topic, art_name)
            combined_markdown += art_content
            
        time.sleep(1)
        
    logger.info("JIRA documentation scraping task complete.")
    return combined_markdown
