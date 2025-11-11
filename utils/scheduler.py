from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import time

def setup_scheduler(app, report_generator):
    scheduler = AsyncIOScheduler()
    
    # Ежедневный отчет в 21:00 UTC
    scheduler.add_job(
        lambda: report_generator("day"),
        CronTrigger(hour=21, minute=0),
        id="daily_report"
    )
    
    # Недельный отчет по воскресеньям
    scheduler.add_job(
        lambda: report_generator("week"),
        CronTrigger(day_of_week="sun", hour=21, minute=0),
        id="weekly_report"
    )
    
    # Ежемесячный отчет 1-го числа
    scheduler.add_job(
        lambda: report_generator("month"),
        CronTrigger(day=1, hour=21, minute=0),
        id="monthly_report"
    )
    
    # Полугодовые отчеты
    scheduler.add_job(
        lambda: report_generator("half_year"),
        CronTrigger(month="1,7", day=1, hour=9, minute=0),
        id="half_year_report"
    )
    
    # Годовой отчет
    scheduler.add_job(
        lambda: report_generator("year"),
        CronTrigger(month=12, day=31, hour=12, minute=0),
        id="yearly_report"
    )
    
    scheduler.start()
    return scheduler
