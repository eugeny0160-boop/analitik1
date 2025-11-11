from datetime import datetime, timedelta
import re
from .verifier import verify_claim
from .categorizer import categorize_event, extract_entities
from utils.translator import translate_to_english

MAX_LENGTHS = {
    "day": 2000,
    "week": 4000,
    "month": 8000,
    "half_year": 10000,
    "year": 10000
}

def generate_report(period_type: str, events: list) -> str:
    """Генерация полного отчета по шаблону ТЗ"""
    # Шаг 1: Исполнительное резюме (10% объема)
    exec_summary = generate_exec_summary(events, period_type)
    
    # Шаг 2: ТОП-5 событий (25%)
    top_events = select_top_events(events, period_type)
    top_events_section = format_top_events(top_events, period_type)
    
    # Шаги 3-7: Детальный анализ
    detailed_analysis = generate_detailed_analysis(events, period_type)
    russia_impact = analyze_russia_impact(events)
    eurasia_impact = analyze_eurasia_impact(events)
    global_impact = analyze_global_impact(events)
    forecasts = generate_forecasts(events)
    
    # Сборка финального отчета
    report = f"""
[Аналитическая записка | Период: {period_type_to_russian(period_type)} | Актуально: {datetime.utcnow().strftime('%d.%m.%Y %H:%M UTC')}]

1. ИСПОЛНИТЕЛЬНОЕ РЕЗЮМЕ
{exec_summary}

2. ТОП-5 КРИТИЧЕСКИХ СОБЫТИЙ
{top_events_section}

3. ДЕТАЛЬНЫЙ ТЕМАТИЧЕСКИЙ АНАЛИЗ
{detailed_analysis}

4. УГЛУБЛЕННЫЙ АНАЛИЗ ВЛИЯНИЯ НА РОССИЮ
{russia_impact}

5. ВЛИЯНИЕ НА КИТАЙ И ЕВРАЗИЮ
{eurasia_impact}

6. ГЛОБАЛЬНЫЕ ПОСЛЕДСТВИЯ
{global_impact}

7. ВЫВОДЫ И ПРОГНОЗЫ
{forecasts}
"""
    
    # Контроль объема
    return truncate_to_limit(report, MAX_LENGTHS[period_type])

def period_type_to_russian(period_type: str) -> str:
    mapping = {
        "day": "Сутки",
        "week": "Неделя",
        "month": "Месяц",
        "half_year": "Полгода",
        "year": "Год"
    }
    return mapping.get(period_type, period_type)

def truncate_to_limit(text: str, max_chars: int) -> str:
    """Обрезка текста с сохранением структуры"""
    if len(text) <= max_chars:
        return text
    
    # Сохраняем заголовки и ключевые разделы
    sections = re.split(r'\n\d+\.', text)
    truncated = sections[0]  # Исполком всегда сохраняется полностью
    
    for section in sections[1:]:
        if len(truncated) + len(section) > max_chars * 0.9:  # 90% лимита
            break
        truncated += f"\n{section[:500]}..."  # Обрезаем длинные разделы
    
    return truncated + f"\n\n[Отчет обрезан по техническим ограничениям. Полная версия доступна в аналитической системе.]"
