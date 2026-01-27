import time
import re
from bs4 import BeautifulSoup, Tag, NavigableString
from urllib.parse import urljoin, urlparse
import logging

logger = logging.getLogger(__name__)

def clean_text(text):
    """Clean and normalize text by removing excessive whitespace."""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

class ToddleScraper:
    """Scraper for Toddle documentation (support.toddleapp.com)"""
    
    def __init__(self, driver):
        self.driver = driver
        self.base_url = "https://support.toddleapp.com"
        self.seen_urls = set()

    def scrape_collection(self, collection_url):
        """Scrape all topics and articles from a collection."""
        try:
            self.driver.get(collection_url)
            time.sleep(4)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract collection name (Entity)
            collection_name = self._extract_collection_name(soup)
            logger.info(f"Scraping collection: {collection_name}")
            
            # Find all topics and their articles
            articles_data = []
            topics = self._extract_topics_and_articles(soup, collection_name)
            
            # Scrape each article
            for topic_name, article_links in topics.items():
                logger.info(f"Processing topic: {topic_name} ({len(article_links)} articles)")
                for article_title, article_url in article_links:
                    if article_url in self.seen_urls:
                        continue
                    self.seen_urls.add(article_url)
                    article_data = self.scrape_article(article_url, collection_name, topic_name)
                    if article_data:
                        articles_data.append(article_data)
                    time.sleep(1)
            
            return articles_data
        except Exception as e:
            logger.error(f"Error scraping collection {collection_url}: {e}")
            return []

    def _extract_collection_name(self, soup):
        # 1. Try breadcrumbs (usually richer)
        breadcrumb_els = soup.select('.intercom-breadcrumb a, .breadcrumb a, [data-testid="breadcrumb"] a')
        for a in breadcrumb_els:
            text = clean_text(a.get_text())
            if text and not any(n in text.lower() for n in ['home', 'help center', 'toddle support']):
                return text
                
        # 2. Try specific Toddle/Intercom header
        h1 = soup.select_one('.collection-title, h1')
        if h1:
            h1_text = clean_text(h1.get_text())
            if h1_text and "help center" not in h1_text.lower():
                return h1_text
                
        return "School administrators"

    def _extract_topics_and_articles(self, soup, collection_name):
        topics = {}
        # Target the card/section structure
        sections = soup.select('.intercom-article-list, .collection-section, .card, section')
        
        # Aggressively find all article links on the page
        all_links = soup.find_all('a', href=lambda h: h and '/articles/' in h)
        
        if not sections or not all_links:
            # If no sections, just group everything under "General" or the first H2 found
            current_topic = "General"
            for element in soup.find_all(['h2', 'h3', 'a']):
                if element.name in ['h2', 'h3']:
                    name = clean_text(element.get_text())
                    if name and name.lower() not in [collection_name.lower(), 'articles']:
                        current_topic = name
                elif element.name == 'a' and '/articles/' in element.get('href', ''):
                    if current_topic not in topics: topics[current_topic] = []
                    topics[current_topic].append((clean_text(element.get_text()), urljoin(self.base_url, element['href'])))
        else:
            for section in sections:
                heading = section.find(['h2', 'h3', 'h4'])
                name = clean_text(heading.get_text()) if heading else "General"
                if name.lower() == collection_name.lower() or name.lower() == "articles":
                    name = "General"
                
                links = section.find_all('a', href=lambda h: h and '/articles/' in h)
                if links:
                    article_data = []
                    for l in links:
                        title = clean_text(l.get_text())
                        # Sometimes the link text is just "Read more" or empty
                        if not title or len(title) < 5:
                            # Try to find a heading inside the link or nearby
                            h = l.find(['h3', 'h4', 'span'])
                            if h: title = clean_text(h.get_text())
                        
                        if not title: title = "Untitled Article"
                        article_data.append((title, urljoin(self.base_url, l['href'])))
                    
                    if article_data:
                        if name not in topics: topics[name] = []
                        topics[name].extend(article_data)
        
        # Final fallback: if still empty but we have links, just put them in "General"
        if not topics and all_links:
            topics["General"] = [(clean_text(l.get_text()) or "Untitled Article", urljoin(self.base_url, l['href'])) for l in all_links]
            
        return topics

    def scrape_article(self, url, entity=None, topic=None):
        """Scrape a single article with high-precision hierarchy and content extraction."""
        try:
            self.driver.get(url)
            time.sleep(4)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # 1. BREADCRUMBS / HIERARCHY
            breadcrumb_els = soup.select('.intercom-breadcrumb a, .breadcrumb a, [data-testid="breadcrumb"] a, nav a')
            breadcrumbs = [clean_text(a.get_text()) for a in breadcrumb_els]
            
            noise = ['home', 'help center', 'all collections', 'support', 'toddle help center', 'toddle support']
            clean_breadcrumbs = [b for b in breadcrumbs if b and not any(n in b.lower() for n in noise) and not b.startswith('http') and len(b) > 2]
            
            if not entity:
                if len(clean_breadcrumbs) >= 1:
                    entity = clean_breadcrumbs[0]
                else:
                    entity = "School administrators"
            
            if not topic:
                if len(clean_breadcrumbs) >= 2:
                    topic = clean_breadcrumbs[1]
                elif len(clean_breadcrumbs) == 1 and clean_breadcrumbs[0] != entity:
                    topic = clean_breadcrumbs[0]
                else:
                    topic = "Getting started"
            
            # 2. TITLE
            # Avoid picking up the generic "Help Center" title usually found in the very first h1 or header
            title_el = soup.select_one('.intercom-article-header h1, h1.t-h1, .article-title, .intercom-article-title')
            title = clean_text(title_el.get_text()) if title_el else ""
            if not title or title.lower() in [entity.lower(), 'help center', 'toddle help center']:
                # Look for an h1 that isn't the generic header
                for h1 in soup.find_all('h1'):
                    h1_text = clean_text(h1.get_text())
                    if h1_text and h1_text.lower() not in noise and h1_text != entity:
                        title = h1_text
                        break
            if not title: title = "Untitled Article"
            
            # 3. CONTENT
            content_md = self._extract_article_content(soup)
            
            return {
                "entity": entity,
                "topic": topic,
                "article": title,
                "link": url,
                "content": content_md
            }
        except Exception as e:
            logger.error(f"Error scraping article {url}: {e}")
            return None

    def _extract_article_content(self, soup):
        selectors = ['.intercom-article-body', 'article', '.article-body', '[role="main"]', '.article-content']
        content_div = None
        for s in selectors:
            content_div = soup.select_one(s)
            if content_div: break
        
        if not content_div: return ""
        
        # Decompose noisy bits
        for unwanted in content_div.select('script, style, nav, header, footer, .intercom-reaction-picker, .breadcrumb'):
            unwanted.decompose()
            
        return self._process_element_to_markdown(content_div)

    def _process_element_to_markdown(self, element):
        md = ""
        seen = set()
        for block in element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'pre', 'blockquote', 'div'], recursive=True):
            if block in seen: continue
            classes = str(block.get('class', []))
            if any(s in classes for s in ['breadcrumb', 'nav', 'header', 'footer']): continue
            
            tag, text = block.name, clean_text(block.get_text())
            if not text and tag != 'pre': continue
            
            if tag.startswith('h'):
                md += f"{'#' * int(tag[1])} {text}\n\n"
                self._mark_seen(block, seen)
            elif tag == 'p' and not any(p.name in ['ul', 'ol', 'li'] for p in block.parents):
                md += f"{text}\n\n"
                self._mark_seen(block, seen)
            elif tag in ['ul', 'ol']:
                for i, li in enumerate(block.find_all('li', recursive=False), 1):
                    prefix = f"{i}." if tag == 'ol' else "-"
                    md += f"{prefix} {clean_text(li.get_text())}\n"
                md += "\n"
                self._mark_seen(block, seen)
            elif tag == 'pre':
                md += f"```\n{block.get_text().strip()}\n```\n\n"
                self._mark_seen(block, seen)
            elif tag == 'blockquote':
                md += f"> {text}\n\n"
                self._mark_seen(block, seen)
            elif tag == 'div' and any(c in classes for c in ['note', 'callout', 'alert']):
                md += f"> **Note**: {text}\n\n"
                self._mark_seen(block, seen)
        return md

    def _mark_seen(self, el, seen):
        seen.add(el)
        for child in el.find_all(True): seen.add(child)

def scrape_toddle(url, driver):
    scraper = ToddleScraper(driver)
    if '/collections/' in url or '/topics/' in url:
        articles = scraper.scrape_collection(url)
        return articles, format_articles_to_markdown(articles)
    elif '/articles/' in url:
        article = scraper.scrape_article(url)
        articles = [article] if article else []
        return articles, format_articles_to_markdown(articles)
    return [], "Error: Unsupported Toddle URL format"

def format_articles_to_markdown(articles):
    if not articles: return "No articles found."
    md = f"# Toddle Documentation Export\n\n**Total Articles**: {len(articles)}\n\n---\n\n"
    for a in articles:
        md += f"Entity: {a['entity']}\n\nTopic: {a['topic']}\n\nArticle: {a['article']}\n\nArticle Link: {a['link']}\n\nContent: \n{a['content']}\n\n---\n\n"
    return md
