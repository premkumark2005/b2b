import requests
from config import ZENROWS_API_KEY

def scrape_with_zenrows(url: str) -> str:
    """
    Scrape URL using ZenRows API ONLY.
    Returns HTML content as text.
    """
    if not ZENROWS_API_KEY or ZENROWS_API_KEY == "your_zenrows_api_key_here":
        raise Exception("ZenRows API key not configured. Please set ZENROWS_API_KEY in .env file")
    
    params = {
        "url": url,
        "apikey": ZENROWS_API_KEY
    }
    
    try:
        print(f"Scraping URL: {url}")
        response = requests.get("https://api.zenrows.com/v1/", params=params, timeout=30)
        response.raise_for_status()
        html = response.text
        print(f"Successfully scraped {len(html)} characters")
        return html
    except requests.exceptions.Timeout:
        raise Exception("ZenRows request timed out. The website might be slow to respond.")
    except requests.exceptions.RequestException as e:
        raise Exception(f"ZenRows scraping failed: {str(e)}")
