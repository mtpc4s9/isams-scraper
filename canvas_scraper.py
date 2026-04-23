import requests
from bs4 import BeautifulSoup
import re
import argparse
import time
import os
from markdownify import markdownify as md

def scrape_article(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            return "Failed to fetch article."
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # In Vanilla Knowledge Base, articles usually have a specific wrapper or just 'userContent'
        target = soup.find(class_='userContent')
        if not target:
            target = soup.find('div', class_='ArticleBody')
        if not target:
            # Fallback to finding h1 and getting its parent's parent
            h1 = soup.find('h1')
            if h1 and h1.parent and h1.parent.parent:
                target = h1.parent.parent
            else:
                target = soup.body
                
        # Remove navigation or unwanted elements if necessary
        for el in target.find_all(['nav', 'script', 'style', 'footer']):
            el.decompose()
            
        markdown_content = md(str(target), heading_style="ATX")
        return markdown_content.strip()
    except Exception as e:
        return f"Error extracting article: {e}"

def scrape_category(group_name, base_url, output_file):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    page = 1
    articles_scraped = 0
    
    with open(output_file, 'w', encoding='utf-8') as f:
        while True:
            url = base_url if page == 1 else f"{base_url}/p{page}"
            print(f"Scraping page {page}: {url}")
            r = requests.get(url, headers=headers, timeout=10)
            
            if r.status_code != 200:
                print(f"Failed to fetch {url}. Status code: {r.status_code}")
                break
                
            if 'This category does not have any articles.' in r.text:
                print("Hit end of category (no articles found message).")
                break
                
            soup = BeautifulSoup(r.text, 'html.parser')
            # Extract links to articles
            links = soup.find_all('a', href=re.compile(r'/kb/articles/'))
            
            if not links:
                print("No article links found on this page. Stopping.")
                break
                
            # Filter and deduplicate links
            seen_urls = set()
            valid_links = []
            for a in links:
                href = a.get('href')
                if href and href not in seen_urls:
                    seen_urls.add(href)
                    valid_links.append((a.text.strip(), href))
            
            if not valid_links:
                print("No valid article links found after filtering. Stopping.")
                break
                
            for title, href in valid_links:
                # Resolve relative URLs
                if href.startswith('/'):
                    article_url = f"https://community.instructure.com{href}"
                else:
                    article_url = href
                    
                print(f"  -> Extracting article: {title}")
                content = scrape_article(article_url)
                
                # Format output
                f.write(f"# {title}\n")
                f.write(f"**Category**: \n")
                f.write(f"**Group**: {group_name}\n")
                f.write(f"**Article Link**: {article_url}\n\n")
                f.write(f"{content}\n\n")
                f.write("---\n\n")
                
                articles_scraped += 1
                time.sleep(0.5) # Be nice to the server
                
            page += 1

    print(f"Finished scraping! {articles_scraped} articles saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Canvas LMS Documentation Scraper")
    parser.add_argument("--url", required=True, help="Category URL to scrape")
    
    args = parser.parse_args()
    
    # Extract group name from URL
    # e.g. https://community.instructure.com/en/kb/categories/454-instructors -> instructors -> Instructors
    match = re.search(r'/categories/\d+-(.+?)(?:/p\d+)?(?:/)?$', args.url)
    if match:
        group_name = match.group(1).replace('-', ' ').title()
    else:
        group_name = "Unknown Group"
        
    output_filename = f"{group_name.replace(' ', '_')}_articles.md"
    scrape_category(group_name, args.url, output_filename)
