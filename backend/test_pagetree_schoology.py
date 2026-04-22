import requests
from urllib.parse import urlparse, urljoin

def test_pagetree():
    url = "https://uc.powerschool-docs.com/en/schoology/latest"
    parsed = urlparse(url)
    
    parts = parsed.path.strip('/').split('/')
    category_prefix = "/".join(parts[:2]) if len(parts) >= 2 else parts[0]
    
    pagetree_url = f"{parsed.scheme}://{parsed.netloc}/{category_prefix}/__pagetree.json"
    print(f"Fetching pagetree from: {pagetree_url}")
    
    response = requests.get(pagetree_url)
    if response.status_code == 200:
        data = response.json()
        
        def extract_links(nodes, parent_title="General"):
            links = []
            for node in nodes:
                title = node.get("title", "")
                path = node.get("path", "")
                
                if path:
                    full_url = urljoin(f"{parsed.scheme}://{parsed.netloc}", path)
                    links.append({
                        'url': full_url,
                        'father': parent_title,
                        'son': title,
                        'slug': parts[0]
                    })
                    
                children = node.get("children", [])
                if children:
                    new_father = f"{parent_title} > {title}" if parent_title and parent_title != "General" else title
                    links.extend(extract_links(children, new_father))
            return links
            
        if isinstance(data, list):
            tree_nodes = data
        else:
            tree_nodes = data.get("value", [])
            
        links = extract_links(tree_nodes)
        print(f"Found {len(links)} links.")
        for l in links[:10]:
            print(f"- {l['father']} -> {l['son']}: {l['url']}")
            
        # Check Instructors
        found = [l for l in links if "Instructors" in l['father'] or "Instructors" in l['son']]
        if found:
            print(f"\nFound 'Instructors': {found[0]['father']} -> {found[0]['son']}")
            
    else:
        print(f"Failed: {response.status_code}")

if __name__ == "__main__":
    test_pagetree()
