import os
import logging
from telegram.ext import Application, MessageHandler, filters
from database import save_post, get_posts_by_period, save_analytic_report
from analyzers.report_generator import generate_report
from utils.scheduler import setup_scheduler
from utils.translator import translate_to_english
from analyzers.verifier import extract_url
import asyncio

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()]
)

async def post_handler(update, context):
    """Обработчик постов из каналов"""
    if not update.channel_post:
        return
    
    channel = update.effective_chat.title or update.effective_chat.username
    text = update.channel_post.text or update.channel_post.caption or ""
    
    # Фильтрация: только посты с упоминанием России в первых 100 символах
    if not is_russia_relevant(text):
        return
    
    url = extract_url(text)
    await save_post(channel, text, url)
    logging.info(f"Saved post from {channel}: {text[:50]}...")

def is_russia_relevant(text: str) -> bool:
    """Проверка релевантности России (ТЗ: упоминание в начале текста)"""
    start_text = text[:150].lower()
    russia_keywords = [
        "россия", "российская федерация", "москва", "kremlin", "russia", 
        "russian", "русский", "российский", "россиянин", "rus"
    ]
    return any(kw in start_text for kw in russia_keywords)

async def generate_and_send_report(period_type: str):
    """Генерация и отправка отчета"""
    hours_map = {
        "day": 24,
        "week": 168,
        "month": 720,
        "half_year": 4320,
        "year": 8760
    }
    
    posts = await get_posts_by_period(hours=hours_map[period_type])
    if not posts.data:
        logging.info(f"No posts for {period_type} report")
        return
    
    # Генерация отчета
    report = generate_report(period_type, posts.data)
    
    # Отправка в каналы
    channels = os.getenv("REPORT_CHANNELS", "").split(",")
    for channel in channels:
        if channel.strip():
            try:
                await context.bot.send_message(
                    chat_id=channel.strip(),
                    text=report,
                    parse_mode="Markdown"
                )
                logging.info(f"Sent {period_type} report to {channel}")
            except Exception as e:
                logging.error(f"Failed to send to {channel}: {str(e)}")
    
    # Сохранение в базу
    await save_analytic_report(period_type, report, channels)

def main():
    # Инициализация бота
    application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    
    # Регистрация обработчиков
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.CHANNEL, post_handler))
    
    # Настройка расписания
    setup_scheduler(application, generate_and_send_report)
    
    # Запуск
    logging.info("Bot started successfully")
    application.run_polling()

if __name__ == "__main__":
    main()
