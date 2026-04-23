import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def connect_and_scrape():
    print("Connecting to the existing browser window...")
    
    options = Options()
    # Connect to the browser window opened by login_classlink_debug.py
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        # We don't need a Service if we are attaching to an existing browser
        driver = webdriver.Chrome(options=options)
        
        print("Successfully attached to the existing browser!")
        print(f"Current URL: {driver.current_url}")
        print(f"Current Title: {driver.title}")
        
        url = "https://help.classlink.com/s/topic/0TOUs0000000T0POAU/apps"
        print(f"Navigating to {url}...")
        driver.get(url)
        time.sleep(5)
        
        print("Checking for Load More button and articles...")
        js_data = driver.execute_script("""
            let data = {};
            
            let loadBtns = Array.from(document.querySelectorAll('button')).filter(b => 
                b.innerText.toLowerCase().includes('more') || 
                b.innerText.toLowerCase().includes('view') ||
                b.innerText.toLowerCase().includes('load')
            );
            data.loadBtns = loadBtns.map(b => b.innerText);
            
            let articles = Array.from(document.querySelectorAll('a')).filter(a => a.href && a.href.includes('/s/article/'));
            data.articlesCount = articles.length;
            
            return data;
        """)
        
        print(f"JS Data: {js_data}")
        
        if js_data['loadBtns']:
            print("Clicking Load More...")
            driver.execute_script("""
                let loadBtn = Array.from(document.querySelectorAll('button')).find(b => 
                    b.innerText.toLowerCase().includes('more') || 
                    b.innerText.toLowerCase().includes('load')
                );
                if (loadBtn) {
                    loadBtn.click();
                }
            """)
            time.sleep(5)
            
            articles_after = driver.execute_script("return Array.from(document.querySelectorAll('a')).filter(a => a.href && a.href.includes('/s/article/')).length;")
            print(f"Articles after clicking Load More: {articles_after}")
            
    except Exception as e:
        print(f"Error connecting to browser: {e}")
        print("Make sure the browser window is still open and running with remote-debugging-port=9222.")

if __name__ == "__main__":
    connect_and_scrape()
