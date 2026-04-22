import requests
from urllib.parse import urlparse

def find_pagetree(url):
    parsed = urlparse(url)
    base_domain = f"{parsed.scheme}://{parsed.netloc}"
    parts = parsed.path.strip('/').split('/')
    
    # Try from longest path down to 1 segment
    for i in range(len(parts), 0, -1):
        prefix = "/".join(parts[:i])
        pagetree_url = f"{base_domain}/{prefix}/__pagetree.json"
        print(f"Trying: {pagetree_url}")
        resp = requests.get(pagetree_url)
        if resp.status_code == 200:
            print(f"Found! {pagetree_url}")
            return pagetree_url
            
    return None

find_pagetree("https://uc.powerschool-docs.com/en/schoology/latest")
find_pagetree("https://uc.powerschool-docs.com/performance-matters/latest/get-started")
