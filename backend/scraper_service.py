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
        driver = auth_service.get_driver()
        if not driver:
            return False, "Not authenticated", []

        try:
            driver.get(category_url)
            time.sleep(3) # Wait for page load
            
            # Get all article links
            # This selector needs to be adjusted based on actual Zendesk theme
            # Common pattern: .article-list-item > a, or .category-article > a
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Try to find article links. This is a heuristic.
            # Look for links that contain '/articles/'
            article_links = []
            for a in soup.find_all('a', href=True):
                if '/articles/' in a['href']:
                    full_url = a['href']
                    if not full_url.startswith('http'):
                        # Construct full URL if relative
                        base_url = category_url.split('/hc/')[0]
                        full_url = base_url + full_url
                    if full_url not in article_links:
                        article_links.append(full_url)
            
            logger.info(f"Found {len(article_links)} articles")
            
            articles = []
            markdown_output = ""
            
            for url in article_links:
                article_data = self.scrape_article(driver, url)
                if article_data:
                    articles.append(article_data)
                    markdown_output += self.format_article_markdown(article_data)
            
            return True, "Scraping completed", articles, markdown_output

        except Exception as e:
            logger.error(f"Scrape category error: {str(e)}")
            return False, f"Error: {str(e)}", [], ""

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
