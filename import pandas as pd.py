# In your imports section (ADD THESE NEW IMPORTS)
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests
import pandas as pd
from bs4 import BeautifulSoup
import os

# Create a session with retry logic (ADD THIS BEFORE YOUR LOOP)
session = requests.Session()
retry_strategy = Retry(
    total=3,                      # Retry 3 times
    backoff_factor=1,             # Wait 1, 2, 4 seconds between retries
    status_forcelist=[500, 502, 503, 504]  # Retry on these status codes
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)

# Your existing Excel reading code
df = pd.read_excel(r'C:\Users\virocana\Desktop\Input.xlsx')
urls = df['URL']
url_ids = df['URL_ID']
output_dir = r'C:\Users\virocana\Desktop\extracted_articles'
os.makedirs(output_dir, exist_ok=True)

for url_id, url in zip(url_ids, urls):
    try:
        # MODIFIED REQUEST WITH TIMEOUT
        response = session.get(url, timeout=30)  # 30 second timeout
        
        response.raise_for_status()  # Check HTTP errors
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Your existing content extraction code
        title_tag = soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else "No Title Found"
        
        content_div = soup.find('div', class_='article-content') or \
                     soup.find('article') or \
                     soup.find('div', class_='entry-content')
        
        article_text = content_div.get_text(strip=True) if content_div else "No Content Found"
        
        # Save to file
        with open(f"{output_dir}/{url_id}.txt", 'w', encoding='utf-8') as f:
            f.write(f"Title: {title}\n\n{article_text}")
            
    except requests.exceptions.RequestException as e:
        # ENHANCED ERROR HANDLING
        print(f"ERROR processing {url_id} ({url}): {str(e)}")
        
        with open(f"{output_dir}/{url_id}_FAILED.txt", 'w') as f:
            f.write(f"Error Details: {str(e)}\nURL: {url}")

print("Processing complete. Check the output folder.")
