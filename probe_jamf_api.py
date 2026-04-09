import time
import json
import logging
from backend.auth_service import AuthService

logging.basicConfig(level=logging.INFO)

script_map_api = """
var done = arguments[0];

async function getPages() {
    try {
        let resp = await fetch('/api/khub/maps/MjQbK8Kv6HB7oJlDFn047g/pages');
        let text = await resp.text();
        return text;
    } catch(e) {
        return JSON.stringify({error: e.message});
    }
}

getPages().then(d => done(d)).catch(e => done(JSON.stringify({error: e.message})));
"""

def probe_api():
    auth = AuthService()
    try:
        driver = auth.get_driver(headless=False)
        
        url = "https://learn.jamf.com/r/en-US/jamf-pro-documentation-current/Applications_and_Utilities"
        driver.get(url)
        time.sleep(8)
        
        raw_text = driver.execute_async_script(script_map_api)
        data = json.loads(raw_text)
        
        with open("jamf_map_pages.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Saved jamf_map_pages.json")
        
        # Parse the paginated TOC
        toc = data.get('paginatedToc', [])
        
        def print_tree(nodes, indent=0):
            for node in nodes:
                title = node.get('title', '?')
                slug = node.get('prettyUrl', '').split('/')[-1] if node.get('prettyUrl') else ''
                children = node.get('children', [])
                prefix = "  " * indent
                child_mark = f" [{len(children)} children]" if children else ""
                print(f"{prefix}- {title} ({slug}){child_mark}")
                if children:
                    print_tree(children, indent + 1)
        
        print_tree(toc)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        auth.close()

if __name__ == "__main__":
    probe_api()
