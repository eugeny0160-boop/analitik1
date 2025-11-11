from googletrans import Translator, LANGUAGES
from langdetect import detect
import time
import logging

translator = Translator()

def detect_language(text: str) -> str:
    """Определение языка текста"""
    try:
        lang = detect(text[:500])  # Анализ первых 500 символов
        return lang if lang in ["ru", "en"] else "other"
    except:
        return "other"

def translate_to_english(text: str, max_retries=3) -> str:
    """Перевод на английский с резервными вариантами"""
    if not text.strip():
        return ""
    
    for attempt in range(max_retries):
        try:
            # Пропускаем русский/английский
            if detect_language(text) == "en":
                return text
            
            result = translator.translate(text, src='auto', dest='en')
            return result.text if result else text
        except Exception as e:
            logging.warning(f"Translation error (attempt {attempt+1}): {str(e)}")
            time.sleep(1)
    
    # Резервный вариант при ошибках
    return text[:200] + "..." if len(text) > 200 else text
