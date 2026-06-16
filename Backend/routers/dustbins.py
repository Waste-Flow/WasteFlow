from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from datetime import datetime
from core.database import get_db
from core.config import settings
from models.dustbin import Dustbin, FillLevelHistory
from models.alert import Alert, AlertType, AlertStatus
from schemas.dustbin import DustbinCreate, DustbinUpdate, DustbinResponse, SensorDataInput, FillHistoryResponse
from middleware.role_checker import require_admin, require_admin_or_supervisor, require_any

router = APIRouter(prefix="/dustbins", tags=["Dustbin Management"])

@router.get("/", response_model=List[DustbinResponse])
async def get_all_dustbins(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_any)
):
    result = await db.execute(select(Dustbin).where(Dustbin.is_active == True))
    return result.scalars().all()

@router.post("/", response_model=DustbinResponse)
async def create_dustbin(
    data: DustbinCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin)
):
    existing = await db.execute(select(Dustbin).where(Dustbin.bin_code == data.bin_code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Bin code already exists")

    dustbin = Dustbin(**data.dict())
    db.add(dustbin)
    await db.commit()
    await db.refresh(dustbin)
    return dustbin

@router.get("/{bin_id}", response_model=DustbinResponse)
async def get_dustbin(bin_id: int, db: AsyncSession = Depends(get_db), current_user=Depends(require_any)):
    result = await db.execute(select(Dustbin).where(Dustbin.id == bin_id))
    dustbin = result.scalar_one_or_none()
    if not dustbin:
        raise HTTPException(status_code=404, detail="Dustbin not found")
    return dustbin

@router.put("/{bin_id}", response_model=DustbinResponse)
async def update_dustbin(
    bin_id: int,
    data: DustbinUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin)
):
    result = await db.execute(select(Dustbin).where(Dustbin.id == bin_id))
    dustbin = result.scalar_one_or_none()
    if not dustbin:
        raise HTTPException(status_code=404, detail="Dustbin not found")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(dustbin, field, value)

    await db.commit()
    await db.refresh(dustbin)
    return dustbin

@router.delete("/{bin_id}")
async def delete_dustbin(bin_id: int, db: AsyncSession = Depends(get_db), current_user=Depends(require_admin)):
    result = await db.execute(select(Dustbin).where(Dustbin.id == bin_id))
    dustbin = result.scalar_one_or_none()
    if not dustbin:
        raise HTTPException(status_code=404, detail="Dustbin not found")
    dustbin.is_active = False
    await db.commit()
    return {"message": "Dustbin deactivated"}

@router.post("/sensor-data")
async def receive_sensor_data(data: SensorDataInput, db: AsyncSession = Depends(get_db)):
    """Endpoint called by ESP8266 to submit sensor readings."""
    result = await db.execute(select(Dustbin).where(Dustbin.bin_code == data.bin_code))
    dustbin = result.scalar_one_or_none()
    if not dustbin:
        raise HTTPException(status_code=404, detail="Dustbin not found")

    # Calculate fill level
    fill_percent = ((dustbin.bin_height_cm - data.distance_cm) / dustbin.bin_height_cm) * 100
    fill_percent = max(0.0, min(100.0, round(fill_percent, 2)))

    dustbin.current_distance_cm = data.distance_cm
    dustbin.fill_level_percent = fill_percent
    dustbin.is_full = fill_percent >= settings.FILL_LEVEL_THRESHOLD
    dustbin.last_updated_at = datetime.utcnow()

    # Save history
    history = FillLevelHistory(
        dustbin_id=dustbin.id,
        fill_level_percent=fill_percent,
        distance_cm=data.distance_cm
    )
    db.add(history)

    # Trigger alert if full
    if dustbin.is_full:
        alert = Alert(
            dustbin_id=dustbin.id,
            alert_type=AlertType.bin_full,
            status=AlertStatus.pending,
            message=f"Bin {dustbin.bin_code} at {dustbin.location_name} is {fill_percent}% full.",
            fill_level_at_alert=int(fill_percent)
        )
        db.add(alert)

    await db.commit()
    return {"bin_code": data.bin_code, "fill_level_percent": fill_percent, "is_full": dustbin.is_full}

@router.get("/{bin_id}/history", response_model=List[FillHistoryResponse])
async def get_fill_history(bin_id: int, db: AsyncSession = Depends(get_db), current_user=Depends(require_any)):
    result = await db.execute(
        select(FillLevelHistory).where(FillLevelHistory.dustbin_id == bin_id)
        .order_by(FillLevelHistory.recorded_at.desc()).limit(100)
    )
    return result.scalars().all()

@router.post("/{bin_id}/mark-collected")
async def mark_as_collected(bin_id: int, db: AsyncSession = Depends(get_db), current_user=Depends(require_any)):
    result = await db.execute(select(Dustbin).where(Dustbin.id == bin_id))
    dustbin = result.scalar_one_or_none()
    if not dustbin:
        raise HTTPException(status_code=404, detail="Dustbin not found")
    dustbin.fill_level_percent = 0.0
    dustbin.is_full = False
    dustbin.last_collected_at = datetime.utcnow()
    await db.commit()
    return {"message": f"Bin {dustbin.bin_code} marked as collected"}
