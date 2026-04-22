from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import json

def test():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    url = "https://uc.powerschool-docs.com/performance-matters/latest/get-started"
    driver.get(url)
    time.sleep(5)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    sidebar = soup.select_one('.vp-desktop-navigation__page-tree, .vp-tree__container, .md-sidebar--primary, .sidebar, [role="navigation"], aside, nav.vp-sidebar, .vp-sidebar, nav')
    
    if sidebar:
        a_tags = sidebar.find_all('a', href=True)
        links = [a['href'] for a in a_tags]
        print(f"Found {len(links)} links in sidebar")
        for link in links:
            print(link)
    else:
        print("Sidebar not found")
        
    driver.quit()

if __name__ == "__main__":
    test()
