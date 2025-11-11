# ЗАМЕНИТЕ СУЩЕСТВУЮЩИЕ ИМПОРТЫ NEWSPAPER НА:
from utils.content_extractor import extract_article_content
import re
import requests
from datetime import datetime, timedelta
import logging

# УДАЛИТЕ ФУНКЦИЮ, ИСПОЛЬЗУЮЩУЮ NEWSPAPER:
# def factcheck_claim(claim: str) -> list:
#    ...

# ЗАМЕНИТЕ НА БОЛЕЕ ПРОСТОЙ МЕТОД ВЕРИФИКАЦИИ:
def search_google_news(query: str, max_results: int = 3) -> list:
    """
    Поиск новостей в Google News через API
    """
    try:
        # Использование Bing News API как более надежной альтернативы
        api_key = os.getenv("BING_NEWS_API_KEY")
        if not api_key:
            return []
        
        url = "https://api.bing.microsoft.com/v7.0/news/search"
        headers = {"Ocp-Apim-Subscription-Key": api_key}
        params = {
            "q": query,
            "count": max_results,
            "freshness": "Day",
            "textFormat": "Raw"
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        results = response.json().get("value", [])
        return [item["url"] for item in results if "url" in item][:max_results]
        
    except Exception as e:
        logging.warning(f"Google News search failed: {str(e)}")
        return []
