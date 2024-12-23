# A web-scraping agent with the following features: 
# 1. Can access and dump info from and to google sheets using the google API
# 2. Accesses ONLY meta tags of the website as we are only concerned with the website description 
# 3. Uses beautiful soup to access only meta tags, then passes the scraped information to an LLM (Ollama) to summarize concisely.
# 4. Dumps the summary right next to its corresponding link on the Google Sheet in the same row.

# Imports 
import requests
from bs4 import BeautifulSoup 
import gspread
import json
from google.oauth2.service_account import Credentials

OLLAMA_API_URL = "http://127.0.0.1:11434/api/chat"
MODEL_NAME = "mistral"

# Using Google API credentials to access a particular sheet by its sheet ID, and return all URLs in the sheet
def get_links():
    CREDENTIALS_FILE = "g_api.json"
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    credentials = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    client = gspread.authorize(credentials)
    sheet = client.open("Web Scraper Test").sheet1
    links = sheet.col_values(1)
    print("Fetched Links:", links)
    return links, sheet

# Fetch data (only meta tag description) of the passed collection of URLs using beautiful soup. 
# The way to optimise the process is to access only the metadata, specifically the description tag.
def fetch_website_data(urls):
    results = []
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string if soup.title else "No Title"
            meta_desc = soup.find("meta", attrs={"name": "description"})
            description = meta_desc["content"] if meta_desc else "No Description"
            results.append({"url": url, "title": title, "description": description})
        except Exception as e:
            results.append({"url": url, "error": str(e)})
    return results

# Convert all website descriptions to concise one-line summaries using Ollama Mistral. Then, dump onto sheet.
def convert_to_one_line(websites, sheet):
    for website in websites:
        try:
            description = website.get('description', '')
            
            if description == 'No Description':
                print(f"Skipping: {website['url']} (No Description)")
                continue  

            prompt = f"Summarise the following description in one-line: {description}"
            
            payload = {
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": prompt}],
            }

            response = requests.post(OLLAMA_API_URL, json=payload, stream=True, timeout=120)

            full_response = ""
            for chunk in response.iter_lines():
                if chunk:
                    try:
                        data = json.loads(chunk)
                        full_response += data.get("message", {}).get("content", "")
                    except json.JSONDecodeError:
                        print(f"Non-JSON chunk: {chunk.decode('utf-8')}")
            
            print(f"Summary for {website['url']}: {full_response.strip()}")
            print("-" * 50)

            row_index = sheet.find(website['url']).row
            sheet.update_cell(row_index, 2, full_response.strip())  # Update second column with the summary
            
        except Exception as e:
            print(f"Error processing {website['url']}: {e}")

def main():
    urls, sheet = get_links()
    websites_data = fetch_website_data(urls)
    convert_to_one_line(websites_data, sheet)

if __name__ == "__main__":
    main()
