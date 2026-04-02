import time
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

logger = logging.getLogger(__name__)

def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

class ClassLinkScraper:
    def __init__(self, driver):
        self.driver = driver
        self.base_url = "https://help.classlink.com"
        self.seen_urls = set()

    def scrape_topic(self, topic_url, topic_category):
        """Scrape all articles from a specific topic URL."""
        logger.info(f"Loading Topic: {topic_url} ({topic_category})")
        
        try:
            self.driver.get(topic_url)
            time.sleep(5) # wait for render
            
            # Try to get expected article count from the value div
            expected_count = self._get_expected_article_count()
            if expected_count:
                logger.info(f"Expected article count: {expected_count}")
            
            # Click 'Load More' / 'View More' until all articles are loaded
            self._expand_all_articles(expected_count)
            
            # Now collect all article links using both BeautifulSoup and Selenium
            article_links = self._collect_article_links()
                    
            logger.info(f"Found {len(article_links)} articles in topic {topic_category}")
            
            articles_data = []
            for url in article_links:
                if url in self.seen_urls:
                    continue
                self.seen_urls.add(url)
                
                article_data = self.scrape_article(url, topic_category)
                if article_data:
                    articles_data.append(article_data)
                time.sleep(1) # polite delay
                
            return articles_data
            
        except Exception as e:
            logger.error(f"Error scraping topic {topic_url}: {e}")
            return []

    def _get_expected_article_count(self):
        """Extract expected article count from: <div aria-hidden="true" class="value" ...>18</div>"""
        try:
            # Method 1: Selenium find_element
            value_divs = self.driver.find_elements(By.CSS_SELECTOR, 'div.value[aria-hidden="true"]')
            for div in value_divs:
                text = div.text.strip()
                if text.isdigit():
                    return int(text)
            
            # Method 2: JS fallback
            result = self.driver.execute_script("""
                let divs = document.querySelectorAll('div.value[aria-hidden="true"]');
                for (let d of divs) {
                    let t = d.innerText.trim();
                    if (/^\\d+$/.test(t)) return parseInt(t);
                }
                return null;
            """)
            return result
        except Exception as e:
            logger.warning(f"Could not get expected article count: {e}")
            return None

    def _collect_article_links(self):
        """Collect article links from both BS4 and Selenium after expanding."""
        article_links = set()
        
        # Method 1: BeautifulSoup parsing
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/s/article/' in href:
                full_url = urljoin(self.base_url, href)
                article_links.add(full_url)
        
        # Method 2: Selenium direct element search (data-special-link)
        try:
            sel_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/s/article/"]')
            for link in sel_links:
                href = link.get_attribute('href')
                if href and '/s/article/' in href:
                    article_links.add(href)
        except Exception:
            pass
            
        # Method 3: JS-based extraction (catches LWC-rendered links)
        try:
            js_links = self.driver.execute_script("""
                let links = [];
                document.querySelectorAll('a[href*="/s/article/"]').forEach(a => {
                    links.push(a.href);
                });
                return links;
            """)
            for href in (js_links or []):
                if '/s/article/' in href:
                    article_links.add(href)
        except Exception:
            pass
            
        return article_links

    def _expand_all_articles(self, expected_count=None):
        """Clicks any 'Load More' buttons until all articles are loaded."""
        iterations = 0
        max_iterations = 20
        
        while iterations < max_iterations:
            # Check if we've loaded enough articles
            if expected_count:
                current_count = len(self._collect_article_links())
                if current_count >= expected_count:
                    logger.info(f"All {current_count}/{expected_count} articles loaded.")
                    break
            
            try:
                # Look for Load More button using the user-specified class
                buttons = self.driver.find_elements(By.XPATH, 
                    "//button[contains(@class, 'slds-button') and ("
                    "contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'load more') or "
                    "contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'view more'))]"
                )
                visible_button = None
                for b in buttons:
                    if b.is_displayed():
                        visible_button = b
                        break
                        
                if not visible_button:
                    break
                    
                logger.info(f"Clicking Load More button (iteration {iterations + 1})...")
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", visible_button)
                time.sleep(1)
                visible_button.click()
                time.sleep(3)
                iterations += 1
            except Exception:
                break

    def scrape_article(self, url, topic_category):
        """Scrape product, audience, title, content, and related articles."""
        logger.info(f"Scraping article: {url}")
        try:
            self.driver.get(url)
            time.sleep(3)
            
            # Scroll down gradually to trigger lazy loading of Related Articles
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.3);")
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.6);")
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
            # Wait a bit more for Related Articles LWC component to render
            time.sleep(2)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # TITLE
            title_el = soup.select_one('h2.article-head')
            if not title_el:
                title_el = soup.select_one('.article-head') or soup.find('h1')
            title = clean_text(title_el.get_text()) if title_el else "Untitled Article"
            
            # PRODUCT & AUDIENCE
            product = "Unknown Product"
            audience = "Unknown Audience"
            
            # Extract using specific article-info-label classes
            labels = soup.find_all('span', class_='article-info-label')
            for label in labels:
                label_text = label.get_text(strip=True).lower()
                if 'product' in label_text:
                    if label.next_sibling and isinstance(label.next_sibling, str):
                        product = clean_text(label.next_sibling)
                elif 'audience' in label_text:
                    if label.next_sibling and isinstance(label.next_sibling, str):
                        audience = clean_text(label.next_sibling)
                        
            # If not found via labels, try improved regex on full text
            full_text = clean_text(soup.get_text(separator=' '))
            if product == "Unknown Product":
                prod_match = re.search(r'Products?:?\s*([A-Za-z0-9_ -]+?)(?=\s*Audience:|\s*[A-Z][a-z]+:|\s*$)', full_text, re.IGNORECASE)
                if prod_match:
                    product = prod_match.group(1).strip()
                    
            if audience == "Unknown Audience":
                aud_match = re.search(r'Audience:?\s*([A-Za-z0-9_ -]+?)(?=\s*[A-Z][a-z]+:|\s*$)', full_text, re.IGNORECASE)
                if aud_match:
                    audience_raw = aud_match.group(1).strip()
                    audience_list = ["Everyone", "Instructor", "Tenant Administrator", "Administrator", "Student", "Parent"]
                    for a in audience_list:
                        if a.lower() in audience_raw.lower():
                            audience = a
                            break
                    if audience == "Unknown Audience" and len(audience_raw) < 30:
                        audience = audience_raw
                    
            # Fallback if product/audience not found in content text
            if product == "Unknown Product":
                topic_lower = topic_category.lower()
                if "launchpad" in topic_lower:
                    product = "LaunchPad"
                elif "cmc" in topic_lower:
                    product = "CMC"
                    
            if audience == "Unknown Audience":
                topic_lower = topic_category.lower()
                if "admin" in topic_lower or "cmc" in topic_lower:
                    audience = "Administrator"
                elif "student" in topic_lower:
                    audience = "Student"
                elif "parent" in topic_lower:
                    audience = "Parent"
                elif "instructor" in topic_lower or "teacher" in topic_lower:
                    audience = "Instructor"
                        
            # CONTENT
            content_div = soup.select_one('.article-column .content') or \
                          soup.select_one('.selfServiceArticleLayout') or \
                          soup.select_one('.uiOutputRichText') or \
                          soup.select_one('.forceOutputRichText') or \
                          soup.find('article')
            if not content_div:
                content_div = soup.find('body')
                
            # Clean out script, style, nav, related articles container
            for unwanted in content_div.select('script, style, nav, .forceTopicTopicList, .selfServiceArticleHeaderDetail'):
                unwanted.decompose()
                
            content_md = self._process_element_to_markdown(content_div)
            
            # RELATED ARTICLES - Use multiple extraction methods
            related_articles = self._extract_related_articles(url)
            
            return {
                "product": product,
                "audience": audience,
                "topic_category": topic_category,
                "article_name": title,
                "article_link": url,
                "content": content_md,
                "related_articles": related_articles
            }
            
        except Exception as e:
            logger.error(f"Error scraping article {url}: {e}")
            return None

    def _extract_related_articles(self, current_url):
        """Extract related articles using multiple methods to handle Shadow DOM and LWC."""
        related_articles = []
        
        # Method 1: JavaScript - query data-special-link elements (most reliable)
        try:
            js_related = self.driver.execute_script("""
                let results = [];
                
                // Method A: data-special-link="true" links
                document.querySelectorAll('a[data-special-link="true"]').forEach(a => {
                    let href = a.href || '';
                    let text = a.innerText ? a.innerText.trim() : '';
                    if (href.includes('/s/article/') && text) {
                        results.push({text: text, href: href});
                    }
                });
                
                // Method B: Links inside a container that follows "Related Articles" heading
                let headings = document.querySelectorAll('h2, h3, div');
                for (let h of headings) {
                    if (h.innerText && h.innerText.trim().toLowerCase().includes('related articles')) {
                        // Get the parent container and find all article links within
                        let container = h.parentElement;
                        if (container) {
                            container.querySelectorAll('a[href*="/s/article/"]').forEach(a => {
                                let href = a.href || '';
                                let text = a.innerText ? a.innerText.trim() : '';
                                if (href && text && !results.some(r => r.href === href)) {
                                    results.push({text: text, href: href});
                                }
                            });
                        }
                        break;
                    }
                }
                
                return results;
            """)
            
            for item in (js_related or []):
                href = item.get('href', '')
                text = item.get('text', '')
                if href and '/s/article/' in href and href != current_url:
                    if not any(x['link'] == href for x in related_articles):
                        related_articles.append({'name': text, 'link': href})
        except Exception as e:
            logger.warning(f"JS related articles extraction failed: {e}")
        
        # Method 2: Selenium direct CSS selector
        if not related_articles:
            try:
                sel_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[data-special-link="true"]')
                for r in sel_links:
                    try:
                        r_href = r.get_attribute('href')
                        r_text = clean_text(r.text)
                        if r_href and '/s/article/' in r_href and r_href != current_url:
                            if not any(x['link'] == r_href for x in related_articles):
                                related_articles.append({'name': r_text, 'link': r_href})
                    except Exception:
                        pass
            except Exception as e:
                logger.warning(f"Selenium related articles extraction failed: {e}")
        
        # Method 3: BeautifulSoup fallback - find links near "Related Articles" text
        if not related_articles:
            try:
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                
                # Find Related Articles heading
                related_heading = None
                for el in soup.find_all(['h2', 'h3', 'div']):
                    if 'related articles' in el.get_text(strip=True).lower():
                        related_heading = el
                        break
                
                if related_heading:
                    # Get parent container and find article links
                    container = related_heading.parent
                    for a in container.find_all('a', href=True):
                        if '/s/article/' in a['href']:
                            href = urljoin(self.base_url, a['href'])
                            text = clean_text(a.get_text())
                            if text and href != current_url:
                                if not any(x['link'] == href for x in related_articles):
                                    related_articles.append({'name': text, 'link': href})
            except Exception as e:
                logger.warning(f"BS4 related articles extraction failed: {e}")
        
        logger.info(f"Found {len(related_articles)} related articles for {current_url}")
        return related_articles

    def _process_element_to_markdown(self, element):
        md = ""
        seen = set()
        for block in element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'pre', 'blockquote', 'div'], recursive=True):
            if block in seen: continue
            classes = str(block.get('class', []))
            if 'forceTopicTopicList' in classes or 'related' in classes.lower(): continue
            
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
                
        return md.strip()

    def _mark_seen(self, el, seen):
        seen.add(el)
        for child in el.find_all(True): seen.add(child)

def scrape_classlink(url, topic_name, driver):
    scraper = ClassLinkScraper(driver)
    
    if '/article/' in url:
        article = scraper.scrape_article(url, topic_name)
        articles = [article] if article else []
    else:
        # treat as topic
        articles = scraper.scrape_topic(url, topic_name)
        
    return articles, format_articles_to_markdown(articles)

def format_articles_to_markdown(articles):
    if not articles: return "No articles found."
    
    md = f"# ClassLink Documentation Export\n\n**Total Articles**: {len(articles)}\n\n---\n\n"
    for a in articles:
        md += f"Product: {a.get('product', 'Unknown')}\n\n"
        md += f"Audience: {a.get('audience', 'Unknown')}\n\n"
        md += f"Topic Category: {a.get('topic_category', 'Unknown')}\n\n"
        md += f"Article Name: {a.get('article_name', 'Unknown')}\n\n"
        md += f"Article Link: {a.get('article_link', '')}\n\n"
        
        md += f"Related Articles:\n"
        for r in a.get('related_articles', []):
            md += f"- [{r['name']}]({r['link']})\n"
        md += "\n"
        
        md += f"Content:\n{a.get('content', '')}\n\n"
        md += "---\n\n"
        
    return md

