import requests
from bs4 import BeautifulSoup
import html2text
import logging
import re
from urllib.parse import urlparse

def extract_article_content(url: str) -> dict:
    """
    Безопасное извлечение контента статьи без newspaper3k и lxml
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        
        # Валидация URL
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return {"error": "Invalid URL format"}
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Определение кодировки
        response.encoding = response.apparent_encoding
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Удаление нежелательных элементов
        for element in soup(['script', 'style', 'iframe', 'nav', 'header', 'footer', 'aside', 'form', 'button']):
            element.decompose()
        
        # Извлечение заголовка
        title = ""
        for tag in ['h1', 'title', 'header']:
            if found := soup.find(tag):
                title = found.get_text().strip()
                break
        if not title and soup.title:
            title = soup.title.string.strip() if soup.title.string else ""
        
        # Извлечение основного контента
        main_content = soup.find('main') or soup.find('article') or soup.find(id=re.compile('content|main|article', re.I))
        
        if not main_content:
            # Фолбэк: берем все параграфы на странице
            paragraphs = soup.find_all('p')
        else:
            paragraphs = main_content.find_all('p')
        
        # Фильтрация коротких и нерелевантных параграфов
        filtered_paragraphs = [
            p.get_text().strip() for p in paragraphs
            if len(p.get_text().strip()) > 60 and not re.search(r'(подпис|реклам|баннер|cookie|cookies)', p.get_text().lower())
        ]
        
        # Преобразование HTML в чистый текст
        h = html2text.HTML2Text()
        h.ignore_links = True
        h.ignore_images = True
        h.ignore_emphasis = True
        h.body_width = 0  # Отключение переноса строк
        
        content = " ".join(filtered_paragraphs[:15])  # Первые 15 значимых абзацев
        
        return {
            "title": title[:200],  # Ограничение длины заголовка
            "text": content[:5000],  # Ограничение длины контента
            "url": url,
            "domain": parsed.netloc,
            "success": True
        }
        
    except Exception as e:
        logging.error(f"Content extraction failed for {url}: {str(e)}")
        return {
            "error": str(e),
            "url": url,
            "success": False,
            "title": "",
            "text": ""
        }
