
import requests
from serpapi import GoogleSearch
from bs4 import BeautifulSoup

# research agent """
class EnhancedResearchAgent:
    def __init__(self, serpapi_key):
        self.serpapi_key = serpapi_key

    def get_full_content(self, url: str) -> str:
        """Extracts article content from a given URL."""
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            paragraphs = soup.find_all('p')
            content = " ".join([para.text for para in paragraphs])
            return " ".join(content.replace("\n", " ").replace("\r", "").split())
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
            return ""

    def web_scrape(self, query: str) -> str:
        print("\033[92m Searching for articles \033[0m")
        params = {
            "q": query, 
            "api_key": self.serpapi_key, 
            "engine": "google", 
            "num": 5,
        }
        search = GoogleSearch(params)
        results = search.get_dict()

        scraped_content = []
        for result in results.get("organic_results", []):
            if "link" in result:
                article_url = result["link"]
                print(f"🔍 Scraping: {article_url}")
                content = self.get_full_content(article_url)
                if content:
                    scraped_content.append(content)

        return "\n".join(scraped_content) if scraped_content else "No relevant data found."

