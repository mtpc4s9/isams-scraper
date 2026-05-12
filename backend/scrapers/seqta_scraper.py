import time
from urllib.parse import urlparse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import markdownify

class SeqtaScraper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    def scrape_article(self, url: str, category: str = "") -> dict:
        """Extracts content from a single SEQTA article page."""
        self.driver.get(url)
        print(f"INFO: Loading article {url}")
        
        try:
            # Wait for either the article title or content to appear
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1, h2.article-head, .slds-rich-text-editor__output"))
            )
            time.sleep(2) # Give LWC time to fully render
            
            # Extract Title
            title = "Unknown Article"
            try:
                title_elem = self.driver.find_element(By.CSS_SELECTOR, "h1, h2.article-head")
                title = title_elem.text.strip()
            except NoSuchElementException:
                pass

            # Extract Content
            content_html = ""
            try:
                content_elem = self.driver.find_element(By.CSS_SELECTOR, ".slds-rich-text-editor__output")
                content_html = content_elem.get_attribute("innerHTML")
            except NoSuchElementException:
                print(f"WARNING: Could not find main content for {url}")
            
            # Convert HTML to Markdown
            clean_md = self._html_to_markdown(content_html)
            
            return {
                "category": category,
                "article_name": title,
                "article_link": url,
                "content": clean_md
            }
            
        except TimeoutException:
            print(f"ERROR: Timeout loading article {url}")
            return None
        except Exception as e:
            print(f"ERROR: Failed to scrape {url}: {e}")
            return None

    def scrape_topic(self, url: str, category: str = "") -> tuple[list, str]:
        """Navigates a topic page, expands all articles, and scrapes each one."""
        self.driver.get(url)
        print(f"INFO: Loading topic {url}")
        
        try:
            # Wait for article links to appear
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/s/article/']"))
            )
            time.sleep(2)
            
            # Click 'View More' / 'Load More' buttons if present
            iteration = 1
            while iteration < 20: # Failsafe
                try:
                    # Look for load more button
                    buttons = self.driver.find_elements(By.XPATH, 
                        "//button[contains(@class, 'slds-button') and ("
                        "contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'load more') or "
                        "contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'view more'))]"
                    )
                    
                    visible_button = None
                    for b in buttons:
                        if b.is_displayed() and b.is_enabled():
                            visible_button = b
                            break
                            
                    if visible_button:
                        print(f"INFO: Clicking Load More button (iteration {iteration})...")
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", visible_button)
                        time.sleep(1)
                        self.driver.execute_script("arguments[0].click();", visible_button)
                        time.sleep(2) # Wait for new articles to load
                        iteration += 1
                    else:
                        break # No more buttons
                except Exception as e:
                    print(f"WARNING: Error clicking load more: {e}")
                    break
            
            # Collect all article links
            link_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/s/article/']")
            article_urls = []
            for elem in link_elements:
                href = elem.get_attribute("href")
                if href and href not in article_urls:
                    article_urls.append(href)
                    
            print(f"INFO: Found {len(article_urls)} articles in topic")
            
            # Scrape each article
            scraped_articles = []
            for a_url in article_urls:
                data = self.scrape_article(a_url, category)
                if data:
                    scraped_articles.append(data)
                    
            # Generate final Markdown
            return scraped_articles, self._generate_combined_markdown(scraped_articles)
            
        except TimeoutException:
            print(f"ERROR: Timeout loading topic {url}")
            return [], f"Error: Timeout loading topic {url}"

    def _html_to_markdown(self, html_content: str) -> str:
        """Converts HTML to clean Markdown suitable for LLM ingestion."""
        if not html_content:
            return ""
            
        md = markdownify.markdownify(
            html_content,
            heading_style="ATX",
            bullets="-",
            strip=['script', 'style', 'nav', 'header', 'footer', 'iframe']
        )
        
        # Clean up excessive newlines
        lines = md.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line or (cleaned_lines and cleaned_lines[-1]):
                cleaned_lines.append(line)
                
        return '\n'.join(cleaned_lines)

    def _generate_combined_markdown(self, articles: list) -> str:
        """Combines multiple scraped articles into a single Markdown document."""
        if not articles:
            return "No articles found."
            
        md_parts = [f"# SEQTA Documentation Export\n\n**Total Articles**: {len(articles)}\n\n---"]
        
        for article in articles:
            frontmatter = (
                f"---\n"
                f"Category: {article.get('category', 'Unknown')}\n"
                f"Article Name: {article.get('article_name', 'Unknown')}\n"
                f"Article Link: {article.get('article_link', 'Unknown')}\n"
                f"---\n\n"
            )
            content = article.get('content', '')
            md_parts.append(f"{frontmatter}{content}\n\n---")
            
        return "\n".join(md_parts)

def scrape_seqta(url: str, category: str, driver) -> tuple[list, str]:
    """Entry point for SEQTA scraping."""
    scraper = SeqtaScraper(driver)
    
    # Determine if URL is an article or a topic
    if "/s/article/" in url:
        data = scraper.scrape_article(url, category)
        if data:
            md = scraper._generate_combined_markdown([data])
            return [data], md
        return [], "Error: Failed to scrape article"
    elif "/s/topic/" in url or "/s/" in url:
        return scraper.scrape_topic(url, category)
    else:
        return [], f"Error: Unsupported URL format for SEQTA scraper: {url}"
