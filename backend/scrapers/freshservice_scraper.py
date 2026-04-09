import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)

def scrape_freshservice(url: str, topic: str, driver=None) -> str:
    """
    Scrape Freshservice Sub-topic folder.
    - url: The sub-topic url (e.g. https://support.freshservice.com/support/solutions/folders/50000000500)
    - topic: Main topic provided by user.
    """
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
        })
        
        all_article_links = set()
        article_links_ordered = []
        
        current_url = url
        sub_topic = "Unknown Sub-topic"
        
        print(f"Start scraping FreshService folder: {current_url}")
        
        # --- Lặp qua các trang (Pagination) ---
        while current_url:
            print(f"Scraping page: {current_url}")
            response = session.get(current_url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Lấy tên Sub-topic ở trang đầu tiên
            if current_url == url:
                title_tag = soup.title
                if title_tag:
                    # e.g., "New Gen Project Management : Freshservice Support"
                    raw_title = title_tag.text.strip()
                    sub_topic = raw_title.split(" : ")[0] if " : " in raw_title else raw_title
            
            # Lấy tất cả href có chứa '/support/solutions/articles/'
            links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '/support/solutions/articles/' in href and not href.endswith('#'):
                    full_link = urljoin(current_url, href)
                    links.append(full_link)
            
            # Bỏ link trùng lặp trên cùng trang
            for link in links:
                if link not in all_article_links:
                    all_article_links.add(link)
                    article_links_ordered.append(link)
            
            # Tìm link trang tiếp theo (Next)
            next_link_tag = soup.find('a', string=lambda t: t and 'Next' in t)
            if next_link_tag and next_link_tag.has_attr('href'):
                # Kiểm tra nếu link không phải disabled
                parent = next_link_tag.parent
                if parent and 'disabled' in parent.get('class', []):
                    current_url = None
                else:
                    current_url = urljoin(current_url, next_link_tag['href'])
            else:
                current_url = None # Không còn trang nào nữa
                
            time.sleep(1) # Tránh rate limit

        if not article_links_ordered:
            return "Error: No articles found in the provided sub-topic URL."

        print(f"Found {len(article_links_ordered)} articles. Extracting content...")
        
        # --- Bắt đầu trích xuất nội dung từng bài ---
        combined_markdown = ""
        
        for idx, article_url in enumerate(article_links_ordered, 1):
            print(f"Scraping article {idx}/{len(article_links_ordered)}: {article_url}")
            try:
                res = session.get(article_url, timeout=15)
                res.raise_for_status()
                art_soup = BeautifulSoup(res.text, 'html.parser')
                
                # Title
                article_title = "Unknown Article"
                content_element = None
                
                # Fallback selectors cho title
                title_h1 = art_soup.find('h1')
                if title_h1:
                    article_title = title_h1.text.strip()
                elif art_soup.title:
                    article_title = art_soup.title.text.split(" : ")[0].strip()
                    
                # Content selectors
                # Bài viết trên FreshDesk thường nằm trong .article-main, .article-body, .article-content
                article_body = art_soup.find(class_='article-main')
                if not article_body:
                    article_body = art_soup.find(class_='article-body')
                if not article_body:
                    article_body = art_soup.find(class_='article-content')
                
                if article_body:
                    content_element = article_body
                else:
                    content_element = art_soup.find('body') # Thất bại lấy thẻ cha
                
                # Trích xuất Pure text
                if content_element:
                    text_content = content_element.get_text(separator='\n', strip=True)
                else:
                    text_content = "Không thể tìm thấy nội dung văn bản cho bài viết này."
                
                # Khởi tạo định dạng Markdown
                md_block = (
                    f"Main topic: {topic}\n"
                    f"Sub-topic: {sub_topic}\n"
                    f"Article name: {article_title}\n"
                    f"Article link: {article_url}\n\n"
                    f"{text_content}\n"
                    f"---\n"
                )
                combined_markdown += md_block
                
            except Exception as e:
                print(f"Error scraping article {article_url}: {e}")
                
            time.sleep(1) # Tránh rate limit
            
        print("Extraction complete.")
        return combined_markdown
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error: Scrape FreshService failed. Exception: {str(e)}"
