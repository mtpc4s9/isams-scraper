import sys
import os
import time

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from auth_service import auth_service

def debug_collection():
    url = "https://support.toddleapp.com/en/collections/3653139-school-administrators#getting-started"
    print(f"Debugging Collection DOM for: {url}")
    
    driver = auth_service.get_driver()
    driver.get(url)
    time.sleep(10) # Heavy wait
    
    html = driver.page_source
    with open('toddle_collection_debug.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("DONE: HTML saved to toddle_collection_debug.html")

if __name__ == "__main__":
    debug_collection()
