import requests
from bs4 import BeautifulSoup, Tag, NavigableString
from auth_service import auth_service
import time
from models import Article
import logging
import re

logger = logging.getLogger(__name__)

class ScraperService:
    def scrape_category(self, category_url: str):
        # Smart Routing: Detect if this is actually a Toddle URL
        if "toddleapp.com" in category_url:
            logger.info(f"Toddle URL detected in iSAMS scraper: {category_url}. Redirecting...")
            from scrapers.toddle_scraper import scrape_toddle
            driver = auth_service.get_driver()
            if not driver:
                return False, "Browser not initialized. Please click 'Initialize' in the browser or 'Launch Login' first.", [], ""
            
            try:
                articles_list, markdown = scrape_toddle(category_url, driver)
                if "Error:" in markdown:
                    return False, markdown, [], ""
                
                # Convert dicts to Article objects
                articles = []
                for a in articles_list:
                    articles.append(Article(
                        module_name=a.get('entity', 'Unknown'),
                        category_level_1=a.get('topic', 'Unknown'),
                        category_level_2=a.get('topic', 'Unknown'),
                        article_name=a.get('article', 'Untitled'),
                        article_url=a.get('link', ''),
                        content=a.get('content', ''),
                        related_articles=[]
                    ))
                
                return True, f"Successfully scraped {len(articles)} Toddle articles", articles, markdown
            except Exception as e:
                logger.error(f"Toddle delegation error: {str(e)}")
                return False, f"Toddle extraction failed: {str(e)}", [], ""

        driver = auth_service.get_driver()
        if not driver:
            return False, "Browser not initialized. Please click 'Initialize' or 'Launch Login' first.", [], ""

        try:
            # Check if driver is already on the page or needs to navigate
            if driver.current_url != category_url:
                driver.get(category_url)
                time.sleep(3) # Wait for page load
            
            # Get all article links
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Try to find article links. This is a heuristic for Zendesk category pages.
            article_links = []
            for a in soup.find_all('a', href=True):
                if '/articles/' in a['href'] and not any(x in a['href'] for x in ['/requests/', '/login', '/signup']):
                    full_url = a['href']
                    if not full_url.startswith('http'):
                        base_url = category_url.split('/hc/')[0]
                        full_url = base_url + ('' if full_url.startswith('/') else '/') + full_url
                    if full_url not in article_links:
                        article_links.append(full_url)
            
            logger.info(f"Found {len(article_links)} articles")
            
            if not article_links:
                # If no links found, maybe they provided a single article URL?
                if "/articles/" in category_url:
                    article_links = [category_url]
                else:
                    return False, "No articles found on this page. If this is a single article, ensure the URL contains '/articles/'.", [], ""

            articles = []
            markdown_output = ""
            
            for url in article_links:
                article_data = self.scrape_article(driver, url)
                if article_data:
                    articles.append(article_data)
                    markdown_output += self.format_article_markdown(article_data)
            
            return True, f"Successfully scraped {len(articles)} articles", articles, markdown_output

        except Exception as e:
            logger.error(f"Scrape category error: {str(e)}")
            return False, f"Scraping failed: {str(e)}", [], ""

    def scrape_article(self, driver, url):
        try:
            driver.get(url)
            time.sleep(2)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Extract Breadcrumbs
            breadcrumbs = [li.get_text(strip=True) for li in soup.select(".breadcrumbs li")]
            module_name = breadcrumbs[0] if len(breadcrumbs) > 0 else "Unknown"
            cat_level_1 = breadcrumbs[1] if len(breadcrumbs) > 1 else "Unknown"
            cat_level_2 = breadcrumbs[2] if len(breadcrumbs) > 2 else cat_level_1
            
            # Extract Title
            title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "Untitled"
            
            # Extract Content
            content_div = soup.select_one(".article-body")
            if not content_div:
                content_div = soup.select_one("article") # Fallback
            
            content_text = ""
            if content_div:
                # Remove unwanted tags
                for tag in content_div(["script", "style", "img", "video", "iframe"]):
                    tag.decompose()
                
                content_text = self.clean_html_structure(content_div)
                
                # Final cleanup of excessive whitespace
                content_text = re.sub(r'\n\s*\n', '\n\n', content_text)
                content_text = content_text.strip()
            
            # Extract Related Articles
            related = []
            related_section = soup.select(".recent-articles li a, .related-articles li a")
            for link in related_section:
                related.append(link.get_text(strip=True))
                
            return Article(
                module_name=module_name,
                category_level_1=cat_level_1,
                category_level_2=cat_level_2,
                article_name=title,
                article_url=url,
                content=content_text,
                related_articles=related
            )
            
        except Exception as e:
            logger.error(f"Error scraping article {url}: {str(e)}")
            return None

    def clean_html_structure(self, element):
        text = ""
        if not element:
            return ""
        
        for child in element.contents:
            if isinstance(child, NavigableString):
                s = str(child).strip()
                if s:
                    text += s + " "
            elif isinstance(child, Tag):
                if child.name == 'br':
                    text += "\n"
                elif child.name == 'li':
                    text += "\n- " + self.clean_html_structure(child).strip() + "\n"
                elif child.name in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'section', 'article']:
                    text += "\n" + self.clean_html_structure(child).strip() + "\n"
                elif child.name in ['ul', 'ol']:
                    text += "\n" + self.clean_html_structure(child).strip() + "\n"
                else:
                    # Inline tags (span, a, b, i, etc.)
                    text += self.clean_html_structure(child)
        
        return text

    def format_article_markdown(self, article: Article) -> str:
        md = "---\n"
        md += f"## Module Name\n{article.module_name}\n"
        md += f"## Category Level 1\n{article.category_level_1}\n"
        md += f"## Category Level 2\n{article.category_level_2}\n"
        md += f"## Article Name\n{article.article_name}\n"
        md += f"## Article URL\n{article.article_url}\n"
        md += f"## Content\n{article.content}\n"
        md += "## Related Articles\n"
        for rel in article.related_articles:
            md += f"- {rel}\n"
        md += "---\n\n"
        return md

scraper_service = ScraperService()
