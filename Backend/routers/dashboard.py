from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from core.database import get_db
from models.dustbin import Dustbin
from models.alert import Alert, AlertStatus
from models.schedule import CollectionSchedule, ScheduleStatus
from models.user import User, UserRole
from middleware.role_checker import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary")
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Total bins
    total_bins = await db.execute(select(func.count(Dustbin.id)).where(Dustbin.is_active == True))
    total_bins = total_bins.scalar()

    # Full bins
    full_bins = await db.execute(select(func.count(Dustbin.id)).where(Dustbin.is_full == True))
    full_bins = full_bins.scalar()

    # Pending alerts
    pending_alerts = await db.execute(
        select(func.count(Alert.id)).where(Alert.status == AlertStatus.pending)
    )
    pending_alerts = pending_alerts.scalar()

    # Today's schedules
    from datetime import date
    today_schedules = await db.execute(
        select(func.count(CollectionSchedule.id)).where(
            func.date(CollectionSchedule.scheduled_at) == date.today()
        )
    )
    today_schedules = today_schedules.scalar()

    # Total collectors
    collectors = await db.execute(
        select(func.count(User.id)).where(User.role == UserRole.collector, User.is_active == True)
    )
    collectors = collectors.scalar()

    return {
        "total_bins": total_bins,
        "full_bins": full_bins,
        "empty_or_partial_bins": total_bins - full_bins,
        "pending_alerts": pending_alerts,
        "todays_scheduled_collections": today_schedules,
        "active_collectors": collectors
    }

@router.get("/bins-status")
async def get_all_bins_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns all bins with their fill levels for the map/overview."""
    query = select(Dustbin).where(Dustbin.is_active == True)

    # Collectors only see their area bins
    if current_user.role.value == "collector" and current_user.area_assigned:
        query = query.where(Dustbin.area == current_user.area_assigned)

    result = await db.execute(query)
    bins = result.scalars().all()

    return [
        {
            "id": b.id,
            "bin_code": b.bin_code,
            "location_name": b.location_name,
            "latitude": b.latitude,
            "longitude": b.longitude,
            "fill_level_percent": b.fill_level_percent,
            "is_full": b.is_full,
            "area": b.area,
            "last_updated_at": b.last_updated_at
        }
        for b in bins
    ]
