import requests
from urllib.parse import urlparse, urljoin

url = "https://uc.powerschool-docs.com/en/schoology/latest"
parsed = urlparse(url)
base_domain = f"{parsed.scheme}://{parsed.netloc}"
parts = parsed.path.strip('/').split('/')

pagetree_url = None
for i in range(len(parts), 0, -1):
    prefix = "/".join(parts[:i])
    test_url = f"{base_domain}/{prefix}/__pagetree.json"
    resp = requests.get(test_url)
    if resp.status_code == 200:
        pagetree_url = test_url
        data = resp.json()
        break

def extract_links(nodes, parent_title="General"):
    links = []
    for node in nodes:
        title = node.get("title", "")
        path = node.get("path", "")
        
        if path:
            full_url = urljoin(base_domain, path)
            links.append(full_url)
            
        children = node.get("children", [])
        if children:
            new_father = f"{parent_title} > {title}" if parent_title and parent_title != "General" else title
            links.extend(extract_links(children, new_father))
    return links

if pagetree_url:
    tree_nodes = data if isinstance(data, list) else data.get("value", [])
    links = extract_links(tree_nodes)
    print(f"Total links found: {len(links)}")
    for link in links[:10]:
        print(link)
