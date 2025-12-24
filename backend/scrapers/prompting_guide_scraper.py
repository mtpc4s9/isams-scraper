import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def scrape_prompting_guide_article(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract Hierarchy from URL
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip('/').split('/')
        
        levels = {}
        for i, part in enumerate(path_parts[:-1]):
            levels[f"level_{i+1}"] = part.replace('-', ' ').title()
            
        # Article Name
        article_name = ""
        h1 = soup.find('h1')
        if h1:
            article_name = clean_text(h1.get_text())
        else:
            article_name = path_parts[-1].replace('-', ' ').title() if path_parts else "Home"

        # Content
        main_content = soup.find('main')
        content_md = ""
        
        if main_content:
            blocks = main_content.find_all(['h2', 'h3', 'h4', 'p', 'ul', 'ol', 'pre', 'div'], recursive=True)
            
            seen_elements = set()
            i = 0
            while i < len(blocks):
                block = blocks[i]
                if block in seen_elements:
                    i += 1
                    continue
                
                classes = block.get('class', [])
                if any(c in classes for c in ['nextra-breadcrumb', 'nx-mb-8', 'nx-mt-16']):
                    i += 1
                    continue
                
                text = block.get_text().strip()
                
                # Flexible Label Detection (Prompt/Output)
                label_match = re.match(r'^(Prompt|Output):?$', text, re.IGNORECASE)
                if label_match and block.name in ['p', 'em', 'strong']:
                    label_type = label_match.group(1).capitalize()
                    # Try to find the associated code block
                    code_block = None
                    for j in range(i + 1, min(i + 4, len(blocks))):
                        b = blocks[j]
                        if (b.name == 'pre') or (b.name == 'div' and 'nextra-code-block' in b.get('class', [])):
                            code_block = b
                            break
                    
                    if code_block:
                        code = code_block.find('code')
                        code_text = code.get_text().strip() if code else ""
                        lang = code.get('data-language', '') if code else ""
                        
                        # Friendly formatting
                        if '\n' not in code_text and len(code_text) < 150:
                            content_md += f"**{label_type}**: `{code_text}`\n\n"
                        else:
                            content_md += f"**{label_type}**:\n```{lang}\n{code_text}\n```\n\n"
                        
                        seen_elements.add(block)
                        seen_elements.add(code_block)
                        for child in code_block.find_all(True):
                             seen_elements.add(child)
                        
                        # Look Ahead: Is there a second code block immediately following this one?
                        # If so, it might be the Output (if this was a Prompt)
                        if label_type == 'Prompt':
                            next_code = None
                            k = j + 1
                            count = 0
                            while k < len(blocks) and count < 15:
                                b = blocks[k]
                                if b in seen_elements:
                                    k += 1
                                    continue
                                count += 1
                                if (b.name == 'pre') or (b.name == 'div' and 'nextra-code-block' in b.get('class', [])):
                                    next_code = b
                                    break
                                elif b.name == 'p' and b.get_text().strip(): # Stop if there is other text
                                    break
                                k += 1
                            
                            if next_code:
                                n_code = next_code.find('code')
                                n_text = n_code.get_text().strip() if n_code else ""
                                n_lang = n_code.get('data-language', '') if n_code else ""
                                if '\n' not in n_text and len(n_text) < 150:
                                    content_md += f"**Output**: `{n_text}`\n\n"
                                else:
                                    content_md += f"**Output**:\n```{n_lang}\n{n_text}\n```\n\n"
                                seen_elements.add(next_code)
                                for child in next_code.find_all(True):
                                     seen_elements.add(child)
                                i = k + 1
                            else:
                                i = j + 1
                        else:
                            i = j + 1
                        continue

                # Check if it's a code block
                is_code_block = (block.name == 'pre') or (block.name == 'div' and 'nextra-code-block' in classes)
                
                # If it's a div but not a code block, we might not want it directly
                if block.name == 'div' and not is_code_block:
                    i += 1
                    continue
                
                # Mark as seen and skip children to avoid duplication
                seen_elements.add(block)
                for child in block.find_all(True):
                    seen_elements.add(child)
                
                # Process the block
                if block.name in ['h2', 'h3', 'h4']:
                    level = int(block.name[1])
                    title = clean_text(block.get_text()).replace('#', '')
                    content_md += f"{'#' * level} {title}\n\n"
                elif block.name == 'p':
                    # Only if not already processed as label
                    p_text = clean_text(block.get_text())
                    if p_text:
                        content_md += f"{p_text}\n\n"
                elif block.name == 'ul':
                    for li in block.find_all('li', recursive=False):
                        li_text = clean_text(li.get_text())
                        if li_text:
                            content_md += f"- {li_text}\n"
                    content_md += "\n"
                elif block.name == 'ol':
                    for k, li in enumerate(block.find_all('li', recursive=False)):
                        li_text = clean_text(li.get_text())
                        if li_text:
                            content_md += f"{k+1}. {li_text}\n"
                    content_md += "\n"
                elif is_code_block:
                    code = block.find('code')
                    if code:
                        lang = code.get('data-language', '') or ""
                        if not lang:
                            for c in code.get('class', []):
                                if c.startswith('language-'):
                                    lang = c.replace('language-', '')
                                    break
                        code_text = code.get_text()
                        content_md += f"```{lang}\n{code_text}\n```\n\n"
                
                i += 1

        return {
            "url": url,
            "levels": levels,
            "article_name": article_name,
            "content": content_md
        }

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def scrape_prompting_guide(url):
    articles_data = []
    seen_urls = set()
    
    # Scrape the initial URL
    data = scrape_prompting_guide_article(url)
    if data:
        articles_data.append(data)
        seen_urls.add(url)
        
        # Try to find more links
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            sidebar = soup.select_one('.nextra-sidebar-container, .nextra-scrollbar, aside')
            main_tag = soup.find('main')
            
            potential_links = []
            if sidebar:
                potential_links.extend(sidebar.find_all('a', href=True))
            if main_tag:
                potential_links.extend(main_tag.find_all('a', href=True))
                
            # Filter for sub-articles
            # Normalize base URL for comparison
            base_url = url.rstrip('/')
            
            for link in potential_links:
                href = link['href']
                full_url = urljoin(url, href).split('#')[0].rstrip('/')
                
                # Heuristic: must start with the base URL and be a direct sub-path or logically related
                # We also want to avoid going to a completely different section if we are at /introduction
                if full_url.startswith(base_url) and full_url != base_url:
                    if full_url not in seen_urls:
                        # print(f"Found sub-article: {full_url}")
                        seen_urls.add(full_url)
                        
                        sub_data = scrape_prompting_guide_article(full_url)
                        # Only add if it has actual content
                        if sub_data and sub_data['content'].strip():
                            articles_data.append(sub_data)
                            
        except Exception as e:
            print(f"Error finding sub-articles for {url}: {e}")

    # Format Output
    final_md = ""
    for article in articles_data:
        if not article['content'].strip():
            continue
            
        final_md += f"# {article['article_name']}\n"
        final_md += f"**Link**: {article['url']}\n"
        for k, v in article['levels'].items():
            final_md += f"**{k.replace('_', ' ').title()}**: {v}\n"
        final_md += "\n"
        final_md += article['content']
        final_md += "\n---\n\n"
        
    return final_md
