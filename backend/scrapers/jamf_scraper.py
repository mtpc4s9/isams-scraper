import logging
import time
import re
import json
import urllib.parse
from bs4 import BeautifulSoup, NavigableString, Tag, Comment
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

MAP_ID = "MjQbK8Kv6HB7oJlDFn047g"  # Jamf Pro Documentation map ID

class JamfScraper:
    def __init__(self, auth_service):
        self.auth_service = auth_service
        self.driver = None
        self.base_url = "https://learn.jamf.com"
        self._toc_cache = None  # Cache the TOC tree

        # JS: extract article content from Shadow DOM (collects ALL sections, deduplicates)
        self.js_article = """
        function querySelectorAllDeep(selector, root = document) {
            let results = Array.from(root.querySelectorAll(selector));
            let allElements = Array.from(root.querySelectorAll('*'));
            for (let el of allElements) {
                if (el.shadowRoot) {
                    results = results.concat(querySelectorAllDeep(selector, el.shadowRoot));
                }
            }
            return results;
        }

        let data = {title: "", html: "", sectionCount: 0};

        // Title from the rendered H1 inside Shadow DOM
        let titles = querySelectorAllDeep('.ft-title, h1.title');
        for (let t of titles) {
            let txt = (t.innerText || t.textContent || '').trim();
            if (txt && !txt.startsWith('_')) {
                data.title = txt;
                break;
            }
        }

        // Collect ALL topic content elements and deduplicate by content ID or actual text
        let contents = querySelectorAllDeep('ft-reader-topic-content');
        data.sectionCount = contents.length;
        let seen = new Set();
        let allHtml = [];
        for (let contentEl of contents) {
            let html = contentEl.shadowRoot ? contentEl.shadowRoot.innerHTML : contentEl.innerHTML;
            if (!html) continue;
            
            let key = "";
            let idMatch = html.match(/id="(ID-[^"]+)"/);
            if (idMatch) {
                key = idMatch[1];
            } else {
                // Fallback: Use the text content inside the section to bypass identical <style> tags
                let match = html.match(/<section[^>]*>([\s\S]*)<\/section>/);
                let bodyHtml = match ? match[1] : html;
                key = bodyHtml.replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').substring(0, 200).trim();
            }

            if (!seen.has(key) && key.length > 0) {
                seen.add(key);
                allHtml.push(html);
            }
        }
        data.html = allHtml.join('\\n');

        return data;
        """

        # JS: scroll down inside the infinite scroll container to load all content
        self.js_scroll_infinite = """
        function querySelectorAllDeep(selector, root = document) {
            let results = Array.from(root.querySelectorAll(selector));
            let allElements = Array.from(root.querySelectorAll('*'));
            for (let el of allElements) {
                if (el.shadowRoot) {
                    results = results.concat(querySelectorAllDeep(selector, el.shadowRoot));
                }
            }
            return results;
        }

        // Find the scrollable container (ft-infinite-scroll or main content area)
        let scrollContainers = querySelectorAllDeep('ft-infinite-scroll');
        if (scrollContainers.length > 0) {
            let container = scrollContainers[0];
            let sr = container.shadowRoot || container;
            let scrollDiv = sr.querySelector('div') || sr;
            scrollDiv.scrollTop = scrollDiv.scrollHeight;
            return true;
        }
        // Fallback: scroll the whole page
        window.scrollTo(0, document.body.scrollHeight);
        return false;
        """

        # JS: fetch TOC tree from Fluid Topics API
        self.js_fetch_toc = f"""
        var done = arguments[0];
        fetch('/api/khub/maps/{MAP_ID}/pages')
            .then(r => r.json())
            .then(d => done(JSON.stringify(d)))
            .catch(e => done(JSON.stringify({{error: e.message}})));
        """

        # JS: detect map ID dynamically from the page
        self.js_detect_map_id = """
        // Try to find map ID from network requests or page data
        let scripts = document.querySelectorAll('script');
        for (let s of scripts) {
            let match = s.textContent.match(/maps\\/([A-Za-z0-9_~-]{20,})/);
            if (match) return match[1];
        }
        // Fallback: check performance entries
        let entries = performance.getEntriesByType('resource');
        for (let e of entries) {
            let match = e.name.match(/maps\\/([A-Za-z0-9_~-]{20,})/);
            if (match) return match[1];
        }
        return null;
        """

    def setup_driver(self):
        try:
            self.driver = self.auth_service.get_driver(headless=False)
            return True, "Driver initialized successfully"
        except Exception as e:
            msg = f"Failed to get authenticated driver: {str(e)}"
            logger.error(msg)
            return False, msg

    def _ensure_driver(self):
        if not self.driver:
            ok, msg = self.setup_driver()
            if not ok:
                raise RuntimeError(msg)

    # =========== TOC / Structure API ===========

    def _fetch_toc(self):
        """Fetch the full TOC tree from the Fluid Topics API."""
        if self._toc_cache:
            return self._toc_cache

        self._ensure_driver()

        # Navigate to the base to ensure we have session cookies
        if not self.driver.current_url.startswith(self.base_url):
            self.driver.get(self.base_url)
            time.sleep(3)

        # Detect map ID dynamically
        map_id = self.driver.execute_script(self.js_detect_map_id)
        if not map_id:
            map_id = MAP_ID
            logger.info(f"Using default map ID: {map_id}")
        else:
            logger.info(f"Detected map ID: {map_id}")

        # Fetch the TOC
        js = f"""
        var done = arguments[0];
        fetch('/api/khub/maps/{map_id}/pages')
            .then(r => r.json())
            .then(d => done(JSON.stringify(d)))
            .catch(e => done(JSON.stringify({{error: e.message}})));
        """
        raw = self.driver.execute_async_script(js)
        data = json.loads(raw)

        if isinstance(data, dict) and 'error' in data:
            raise RuntimeError(f"Failed to fetch TOC: {data['error']}")

        toc = data.get('paginatedToc', data if isinstance(data, list) else [])
        self._toc_cache = toc
        return toc

    def _find_node_in_toc(self, slug, nodes=None, parent_title=None):
        """
        Recursively search the TOC tree for a node matching the given URL slug.
        Returns (node, parent_title) or (None, None).
        """
        if nodes is None:
            nodes = self._fetch_toc()

        for node in nodes:
            pretty_url = node.get('prettyUrl', '')
            node_slug = pretty_url.rstrip('/').split('/')[-1] if pretty_url else ''
            if node_slug == slug:
                return node, parent_title
            children = node.get('children', [])
            if children:
                found, found_parent = self._find_node_in_toc(slug, children, node.get('title', parent_title))
                if found:
                    return found, found_parent
        return None, None

    def _collect_leaf_urls(self, node):
        """
        Given a TOC node, collect all leaf article prettyUrls (recursing into children).
        If the node itself has content, include it first.
        """
        urls = []
        pretty_url = node.get('prettyUrl', '')
        children = node.get('children', [])

        if pretty_url:
            urls.append({
                'title': node.get('title', ''),
                'url': self.base_url + pretty_url
            })

        for child in children:
            urls.extend(self._collect_leaf_urls(child))

        return urls

    # =========== Scraping Methods ===========

    def _scroll_and_load(self):
        """Scroll the infinite scroll container multiple times to load all content."""
        for i in range(5):  # Scroll up to 5 times
            try:
                self.driver.execute_script(self.js_scroll_infinite)
                time.sleep(2)
            except Exception:
                break

    def _extract_content(self):
        """Navigate, scroll, and extract article content."""
        # Initial wait for SPA render
        time.sleep(8)

        # Scroll to trigger infinite scroll loading
        self._scroll_and_load()

        # Extract content
        raw_data = self.driver.execute_script(self.js_article)
        if not raw_data.get('html'):
            time.sleep(5)
            self._scroll_and_load()
            raw_data = self.driver.execute_script(self.js_article)

        logger.info(f"Extracted {raw_data.get('sectionCount', 0)} section(s)")
        return raw_data

    def scrape_article(self, url):
        """Scrapes an individual Jamf article and determines its group from the TOC tree."""
        self._ensure_driver()

        # Extract slug from URL
        slug = url.rstrip('/').split('/')[-1]

        # Find this article in the TOC tree to get group info
        product = "Jamf Pro"
        group = "General"
        try:
            node, parent_title = self._find_node_in_toc(slug)
            if parent_title:
                group = parent_title
            elif node:
                group = node.get('title', group)
        except Exception as e:
            logger.warning(f"Could not fetch TOC for group detection: {e}")

        # Navigate and extract content
        logger.info(f"Navigating to Jamf URL: {url}")
        self.driver.get(url)

        try:
            raw_data = self._extract_content()

            html_content = raw_data.get('html', '')
            title = raw_data.get('title', '').strip()
            if not title:
                title = slug.replace('_', ' ')

            if not html_content:
                return False, f"Could not find topic content on {url}", None

            markdown_content = self.convert_html_to_markdown(html_content, url)

            result = {
                'product': product,
                'group': group,
                'article_name': title,
                'article_link': url,
                'content': markdown_content
            }
            return True, "Success", result

        except Exception as e:
            logger.error(f"Error scraping article {url}: {e}")
            return False, str(e), None

    def scrape_category(self, url):
        """
        Scrapes all articles within a category/group.
        Detects children from the TOC tree and scrapes each one.
        Returns combined markdown with all articles.
        """
        self._ensure_driver()
        slug = url.rstrip('/').split('/')[-1]

        # Fetch entire TOC
        try:
            toc_data = self._fetch_toc()
            node, parent_title = self._find_node_in_toc(slug, node_list=toc_data)
        except Exception as e:
            return False, f"Failed to fetch TOC: {e}", None

        if not node:
            # Fallback: just scrape as single article
            logger.warning(f"Node '{slug}' not found in TOC, scraping as single article")
            return self.scrape_article(url)

        # Check if this node is the root Map node (e.g. "Jamf Pro Documentation")
        is_root_map = False
        if len(toc_data) > 0 and node.get('title') == toc_data[0].get('title') and not parent_title:
            is_root_map = True

        # Determine the group name
        group_name = parent_title or node.get('title', slug.replace('_', ' '))
        category_title = node.get('title', slug.replace('_', ' '))

        # Collect all article URLs
        article_urls = []
        if is_root_map:
            logger.info(f"Target URL is the root of the TOC Map. Scraping ENTIRE map.")
            group_name = "Jamf Pro Map"
            for top_node in toc_data:
                article_urls.extend(self._collect_leaf_urls(top_node))
        else:
            article_urls = self._collect_leaf_urls(node)
            
        logger.info(f"Category/Map '{category_title}' has {len(article_urls)} articles (including self + children)")

        if len(article_urls) <= 1:
            # This is a leaf node or has no children, scrape as single article
            return self.scrape_article(url)

        # Scrape each article
        all_articles = []
        for idx, article_info in enumerate(article_urls):
            art_url = article_info['url']
            art_title = article_info['title']
            logger.info(f"[{idx+1}/{len(article_urls)}] Scraping: {art_title}")

            try:
                self.driver.get(art_url)

                raw_data = self._extract_content()

                html_content = raw_data.get('html', '')
                title = raw_data.get('title', '').strip() or art_title

                if html_content:
                    md = self.convert_html_to_markdown(html_content, art_url)
                    all_articles.append({
                        'product': 'Jamf Pro',
                        'group': group_name,
                        'article_name': title,
                        'article_link': art_url,
                        'content': md
                    })
                else:
                    logger.warning(f"No content found for {art_url}")
            except Exception as e:
                logger.error(f"Error scraping {art_url}: {e}")

        if not all_articles:
            return False, "No articles could be scraped", None

        # Combine all articles into one markdown document
        combined_md = f"# {category_title}\n\n"
        combined_md += f"**Product:** Jamf Pro  \n"
        combined_md += f"**Group:** {group_name}  \n"
        combined_md += f"**Articles:** {len(all_articles)}  \n\n---\n\n"

        for art in all_articles:
            combined_md += f"## {art['article_name']}\n\n"
            combined_md += f"*Source: [{art['article_link']}]({art['article_link']})*\n\n"
            combined_md += art['content']
            combined_md += "\n\n---\n\n"

        result = {
            'product': 'Jamf Pro',
            'group': group_name,
            'article_name': category_title,
            'article_link': url,
            'content': combined_md
        }
        return True, f"Scraped {len(all_articles)} articles", result

    def get_category_links(self, category_url):
        """Returns all article links within a category from the TOC tree."""
        self._ensure_driver()
        slug = category_url.rstrip('/').split('/')[-1]

        try:
            node, parent_title = self._find_node_in_toc(slug)
            if not node:
                return False, f"Node '{slug}' not found in TOC", []

            urls = self._collect_leaf_urls(node)
            links = [{'title': u['title'], 'link': u['url']} for u in urls]
            logger.info(f"Found {len(links)} links in category '{node.get('title', slug)}'")
            return True, "Success", links
        except Exception as e:
            logger.error(f"Error getting category links: {e}")
            return False, str(e), []

    def close(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None

    # =========== HTML TO MARKDOWN ===========

    def convert_html_to_markdown(self, html_content: str, base_url: str) -> str:
        # Pre-cleanup lit-html artifacts that sometimes appear as text
        html_content = re.sub(r'<\!--\?lit\$[0-9]+\$-->', '', html_content)
        
        soup = BeautifulSoup(html_content, 'html.parser')

        # Strip script, style, and comments
        for tag in soup(["script", "style", "meta", "noscript", "svg"]):
            tag.decompose()

        for comment in soup.findAll(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        markdown = self._process_element(soup, base_url).strip()
        # Post-cleanup lit-html just in case they slipped through as text nodes
        markdown = re.sub(r'\?lit\$[0-9]+\$', '', markdown)
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)
        return markdown

    def _process_element(self, element, base_url: str, list_level=0) -> str:
        if isinstance(element, NavigableString):
            text = str(element).replace('\xa0', ' ')
            if text.strip() or '\n' in text:
                return text
            return ""

        if not hasattr(element, 'name') or element.name is None:
            return ""

        tag = element.name.lower()
        result = ""

        # --- Container Elements ---
        if tag in ['div', 'span', 'section', 'article', 'main', 'header', 'footer']:
            for child in element.children:
                result += self._process_element(child, base_url, list_level)
            if tag in ['div', 'section', 'article'] and result.strip():
                result += "\n\n"
            return result

        # --- Paragraphs & Headings ---
        elif tag == 'p':
            for child in element.children:
                result += self._process_element(child, base_url, list_level)
            return f"{result.strip()}\n\n"

        elif tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(tag[1])
            for child in element.children:
                result += self._process_element(child, base_url, list_level)
            return f"\n{'#' * level} {result.strip()}\n\n"

        # --- Lists ---
        elif tag in ['ul', 'ol']:
            result += "\n"
            for child in element.children:
                if child.name == 'li':
                    item_text = self._process_element(child, base_url, list_level + 1).strip()
                    if item_text:
                        indent = "  " * list_level
                        prefix = "- " if tag == 'ul' else "1. "
                        result += f"{indent}{prefix}{item_text}\n"
            result += "\n"
            return result

        elif tag == 'li':
            for child in element.children:
                result += self._process_element(child, base_url, list_level)
            return result

        # --- Formatting ---
        elif tag in ['strong', 'b']:
            for child in element.children:
                result += self._process_element(child, base_url, list_level)
            return f"**{result.strip()}** " if result.strip() else ""

        elif tag in ['em', 'i']:
            for child in element.children:
                result += self._process_element(child, base_url, list_level)
            return f"*{result.strip()}* " if result.strip() else ""

        elif tag in ['code', 'kbd']:
            for child in element.children:
                result += self._process_element(child, base_url, list_level)
            if '\n' in result:
                return f"\n```\n{result.strip()}\n```\n"
            return f"`{result.strip()}`"

        elif tag == 'pre':
            code_text = element.get_text()
            return f"\n```\n{code_text}\n```\n\n"

        # --- Links & Images ---
        elif tag == 'a':
            href = element.get('href', '')
            if href and not href.startswith(('http://', 'https://', 'mailto:')):
                href = urllib.parse.urljoin(self.base_url, href)

            for child in element.children:
                result += self._process_element(child, base_url, list_level)

            link_text = result.strip()
            if link_text and href:
                return f"[{link_text}]({href})"
            return link_text

        elif tag == 'img':
            src = element.get('src', '')
            alt = element.get('alt', 'Image')
            if src and not src.startswith(('http://', 'https://')):
                src = urllib.parse.urljoin(self.base_url, src)
            if src:
                return f"![{alt}]({src})\n"
            return ""

        # --- Tables ---
        elif tag == 'table':
            rows = element.find_all('tr')
            if not rows:
                return ""

            for i, row in enumerate(rows):
                cols = row.find_all(['th', 'td'])
                if not cols:
                    continue

                row_text = "| " + " | ".join(
                    [self._process_element(c, base_url).strip().replace('\n', ' ') for c in cols]
                ) + " |\n"
                result += row_text

                if i == 0 and row.find('th'):
                    result += "| " + " | ".join(["---" for _ in cols]) + " |\n"

            return f"\n{result}\n"

        # --- Callout/Note blocks ---
        elif tag == 'div' and element.get('class') and any('note' in c for c in element.get('class', [])):
            note_title = element.find(class_='note__title')
            title_text = note_title.get_text().strip() if note_title else "Note"
            if note_title:
                note_title.decompose()
            for child in element.children:
                result += self._process_element(child, base_url, list_level)
            return f"\n> **{title_text}** {result.strip()}\n\n"

        # --- Default ---
        else:
            for child in element.children:
                result += self._process_element(child, base_url, list_level)
            return result
