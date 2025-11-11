import re
import requests
from datetime import datetime, timedelta
from newspaper import Article
from .categorizer import extract_entities

def extract_url(text: str) -> str:
    """Извлечение первой URL из текста"""
    urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', text)
    return urls[0] if urls else ""

async def verify_claim(claim: str, source_url: str = None):
    """
    Верификация утверждения через 3 источника:
    1. Внутренняя база постов
    2. Google News API
    3. Фактчекинговые сайты
    """
    verification_sources = []
    
    # 1. Поиск в базе постов
    supabase_posts = await search_similar_posts(claim)
    verification_sources.extend([p["url"] for p in supabase_posts if p["url"]])
    
    # 2. Поиск в Google News
    if len(verification_sources) < 2:
        news_sources = search_google_news(claim)
        verification_sources.extend(news_sources)
    
    # 3. Фактчекинг (для спорных утверждений)
    if len(verification_sources) < 2 and is_controversial(claim):
        factcheck_sources = factcheck_claim(claim)
        verification_sources.extend(factcheck_sources)
    
    # Фильтрация дубликатов и нерабочих ссылок
    unique_sources = list(dict.fromkeys(verification_sources))
    working_sources = [url for url in unique_sources if is_valid_url(url)]
    
    is_verified = len(working_sources) >= 2
    return is_verified, working_sources[:3]  # Не более 3 источников

def is_controversial(text: str) -> bool:
    """Проверка на спорность утверждения"""
    controversial_keywords = [
        "санкции", "обвиняет", "скандал", "коррупция", "взятка", 
        "нарушил", "запретил", "угрожает", "кризис", "крах"
    ]
    return any(kw in text.lower() for kw in controversial_keywords)

def is_valid_url(url: str) -> bool:
    """Проверка рабочей ссылки"""
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        return response.status_code == 200
    except:
        return False
