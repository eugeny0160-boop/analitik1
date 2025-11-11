# В начало файла добавьте:
from utils.content_extractor import extract_article_content

# ЗАМЕНИТЕ функцию verify_claim В report_generator.py на:
def verify_claim_simplified(claim_text: str, source_url: str = None) -> tuple:
    """
    Упрощенная верификация без newspaper3k
    """
    sources = []
    
    # 1. Если есть исходный URL - добавляем его
    if source_url and "http" in source_url:
        sources.append(source_url)
    
    # 2. Поиск похожих утверждений в базе
    similar_posts = search_similar_posts_in_db(claim_text)
    sources.extend([post["url"] for post in similar_posts if post.get("url")])
    
    # 3. Поиск в новостях
    news_sources = search_google_news(claim_text[:100])  # Первые 100 символов для поиска
    sources.extend(news_sources)
    
    # Удаление дубликатов и пустых URL
    unique_sources = list({url for url in sources if url and "http" in url})
    
    # Валидация источников
    verified_sources = []
    for url in unique_sources[:3]:  # Не более 3 источников
        try:
            result = extract_article_content(url)
            if result.get("success") and len(result.get("text", "")) > 200:
                verified_sources.append(url)
        except Exception as e:
            logging.debug(f"Source validation failed for {url}: {str(e)}")
    
    return len(verified_sources) >= 2, verified_sources[:3]
