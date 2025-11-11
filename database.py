import os
from supabase import create_client, Client
from datetime import datetime, timedelta
import hashlib

# Инициализация Supabase
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def generate_text_hash(text: str) -> str:
    """Генерация хеша для дедупликации"""
    return hashlib.md5(f"{text[:200]}".encode()).hexdigest()

async def save_post(channel: str, text: str, url: str = None, lang: str = "other"):
    """Сохранение поста в базу с дедупликацией"""
    text_hash = generate_text_hash(text)
    
    # Проверка дубликатов за последние 24 часа
    existing = supabase.table("posts")\
        .select("*")\
        .eq("hash", text_hash)\
        .gte("date", (datetime.utcnow() - timedelta(hours=24)).isoformat())\
        .execute()
    
    if existing.data:
        return False
    
    # Определение языка
    detected_lang = detect_language(text) if lang == "other" else lang
    
    # Сохранение
    supabase.table("posts").insert({
        "channel": channel,
        "text": text[:5000],  # Ограничение длины
        "url": url or "",
        "language": detected_lang,
        "date": datetime.utcnow().isoformat(),
        "hash": text_hash
    }).execute()
    return True

async def get_posts_by_period(hours: int = 24):
    """Получение постов за период"""
    return supabase.table("posts")\
        .select("*")\
        .gte("date", (datetime.utcnow() - timedelta(hours=hours)).isoformat())\
        .order("date", desc=True)\
        .execute()

async def save_analytic_report(period_type: str, content: str, channels: list):
    """Сохранение аналитического отчета"""
    content_hash = generate_text_hash(content)
    
    # Проверка дубликатов
    existing = supabase.table("analytics")\
        .select("*")\
        .eq("period_type", period_type)\
        .eq("content_hash", content_hash)\
        .execute()
    
    if existing.data:
        return False
    
    supabase.table("analytics").insert({
        "period_type": period_type,
        "content": content,
        "content_hash": content_hash,
        "sent_channels": channels
    }).execute()
    return True
