from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def test():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    url = "https://uc.powerschool-docs.com/performance-matters/latest/get-started"
    driver.get(url)
    time.sleep(5)
    
    # Dump window variables
    logs = driver.execute_script("""
        let out = {};
        for (let key in window) {
            try {
                if (key.includes('__') || key.includes('data') || key.includes('route') || key.includes('tree') || key.includes('doc')) {
                    if (typeof window[key] === 'object' && window[key] !== null) {
                        out[key] = true;
                    }
                }
            } catch (e) {}
        }
        return out;
    """)
    print("Found potential window objects:", logs)
    
    # Try to see if there are buttons/spans that toggle the sidebar tree
    toggles = driver.execute_script("""
        return Array.from(document.querySelectorAll('.v-icon, button, summary, .vp-tree-item__toggle, .caret')).map(e => e.outerHTML).slice(0, 5);
    """)
    print("Toggles:", toggles)

    driver.quit()

if __name__ == "__main__":
    test()
