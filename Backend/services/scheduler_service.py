from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
from datetime import datetime, timedelta

scheduler = AsyncIOScheduler()

def start_scheduler():
    scheduler.add_job(check_overdue_collections, "interval", hours=1, id="overdue_check")
    scheduler.add_job(daily_report_summary, "cron", hour=8, minute=0, id="daily_report")
    scheduler.start()
    logger.info("Scheduler started")

async def check_overdue_collections():
    """Flag schedules that were not completed on time."""
    logger.info("Checking overdue collections...")
    # Import here to avoid circular imports
    from core.database import AsyncSessionLocal
    from sqlalchemy.future import select
    from models.schedule import CollectionSchedule, ScheduleStatus

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(CollectionSchedule).where(
                CollectionSchedule.status == ScheduleStatus.pending,
                CollectionSchedule.scheduled_at < datetime.utcnow() - timedelta(hours=2)
            )
        )
        overdue = result.scalars().all()
        for schedule in overdue:
            schedule.status = ScheduleStatus.missed
        await db.commit()
        logger.info(f"{len(overdue)} overdue schedules marked as missed")

async def daily_report_summary():
    """Runs every morning at 8am — log a summary."""
    logger.info(f"[Daily Report] Running at {datetime.utcnow()}")
