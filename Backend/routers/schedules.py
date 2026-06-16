from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from datetime import datetime
from core.database import get_db
from models.schedule import CollectionSchedule, ScheduleStatus
from models.user import User, UserRole
from schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleResponse
from middleware.role_checker import require_admin_or_supervisor, require_any

router = APIRouter(prefix="/schedules", tags=["Collection Scheduling"])

@router.get("/", response_model=List[ScheduleResponse])
async def get_schedules(db: AsyncSession = Depends(get_db), current_user: User = Depends(require_any)):
    query = select(CollectionSchedule).order_by(CollectionSchedule.scheduled_at)

    # Collectors see only their own schedules
    if current_user.role == UserRole.collector:
        query = query.where(CollectionSchedule.collector_id == current_user.id)

    result = await db.execute(query)
    return result.scalars().all()

@router.post("/", response_model=ScheduleResponse)
async def create_schedule(
    data: ScheduleCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin_or_supervisor)
):
    schedule = CollectionSchedule(**data.dict())
    db.add(schedule)
    await db.commit()
    await db.refresh(schedule)
    return schedule

@router.put("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: int,
    data: ScheduleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_any)
):
    result = await db.execute(select(CollectionSchedule).where(CollectionSchedule.id == schedule_id))
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(schedule, field, value)

    if data.status == ScheduleStatus.completed:
        schedule.completed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(schedule)
    return schedule

@router.delete("/{schedule_id}")
async def delete_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin_or_supervisor)
):
    result = await db.execute(select(CollectionSchedule).where(CollectionSchedule.id == schedule_id))
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    await db.delete(schedule)
    await db.commit()
    return {"message": "Schedule deleted"}
