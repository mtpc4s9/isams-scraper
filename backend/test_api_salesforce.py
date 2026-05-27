from fastapi.testclient import TestClient
import json
import sys
import os

# Adjust path to import backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import FastAPI app from main.py
try:
    from backend.main import app
except ImportError:
    # Try alternate path just in case
    from main import app

client = TestClient(app)

def test_api_scrape_salesforce():
    payload = {
        "url": "https://www.salesforce.com/eu/learning-centre/customer-service/",
        "module": "Customer Service"
    }
    
    print("Sending POST request to /scrape-salesforce...")
    response = client.post("/scrape-salesforce", json=payload)
    
    print(f"Response status code: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    print(f"Success state: {data.get('success')}")
    print(f"Message: {data.get('message')}")
    
    markdown_content = data.get('markdown_content')
    print(f"Markdown content size: {len(markdown_content)} characters")
    
    # Save the output to verify manually
    output_path = "c:\\Users\\TruongPhan\\.gemini\\antigravity\\scratch\\isams-scraper\\backend\\test_api_salesforce_output.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"Successfully wrote response to {output_path}")

if __name__ == "__main__":
    test_api_scrape_salesforce()
