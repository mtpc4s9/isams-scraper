import os
import re
import argparse
import logging
from urllib.parse import urlparse
from backend.auth_service import auth_service
from backend.scrapers.jamf_scraper import JamfScraper

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def sanitize_filename(name):
    clean_name = re.sub(r'[\\/*?:"<>|\r\n]', "", name)
    return clean_name.strip().replace(' ', '_')

def save_result(result, output_dir):
    """Save a single scrape result to a markdown file."""
    product = result['product']
    group = result['group']
    article_name = result['article_name']
    link = result['article_link']
    content = result['content']

    # Build markdown with frontmatter
    md = f"---\n"
    md += f"Product: {product}\n"
    md += f"Group: {group}\n"
    md += f"Article Name: {article_name}\n"
    md += f"Article Link: {link}\n"
    md += f"---\n\n"
    md += content

    # Save to file
    safe_product = sanitize_filename(product)
    safe_group = sanitize_filename(group)
    safe_article = sanitize_filename(article_name)

    dir_path = os.path.join(output_dir, safe_product, safe_group)
    os.makedirs(dir_path, exist_ok=True)

    file_path = os.path.join(dir_path, f"{safe_article}.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(md)

    logger.info(f"Saved: {file_path}")
    return file_path

def main():
    parser = argparse.ArgumentParser(description="Jamf Learn Documentation Scraper")
    parser.add_argument("url", help="URL of the Jamf article or category")
    parser.add_argument("--single", action="store_true",
                        help="Force scraping as a single article (ignore children)")
    parser.add_argument("--output", default="jamf_docs", help="Output directory folder")

    args = parser.parse_args()

    scraper = JamfScraper(auth_service)

    try:
        if args.single:
            logger.info("Single article mode.")
            ok, msg, result = scraper.scrape_article(args.url)
            if not ok:
                logger.error(f"Failed: {msg}")
                return
            save_result(result, args.output)
        else:
            logger.info("Auto mode: detecting children from TOC tree...")
            ok, msg, result = scraper.scrape_category(args.url)
            if not ok:
                logger.error(f"Failed: {msg}")
                return
            save_result(result, args.output)
            logger.info(f"Done. {msg}")

    finally:
        scraper.close()
        auth_service.close()

if __name__ == "__main__":
    main()
