from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from datetime import datetime
from core.database import get_db
from models.alert import Alert, AlertStatus
from schemas.alert import AlertResponse, AlertUpdateStatus
from middleware.role_checker import require_any, require_admin_or_supervisor

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("/", response_model=List[AlertResponse])
async def get_all_alerts(db: AsyncSession = Depends(get_db), current_user=Depends(require_any)):
    result = await db.execute(select(Alert).order_by(Alert.created_at.desc()))
    return result.scalars().all()

@router.get("/pending", response_model=List[AlertResponse])
async def get_pending_alerts(db: AsyncSession = Depends(get_db), current_user=Depends(require_any)):
    result = await db.execute(
        select(Alert).where(Alert.status == AlertStatus.pending).order_by(Alert.created_at.desc())
    )
    return result.scalars().all()

@router.put("/{alert_id}/status", response_model=AlertResponse)
async def update_alert_status(
    alert_id: int,
    data: AlertUpdateStatus,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_any)
):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = data.status
    if data.status == AlertStatus.resolved:
        alert.resolved_at = datetime.utcnow()

    await db.commit()
    await db.refresh(alert)
    return alert

@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin_or_supervisor)
):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    await db.delete(alert)
    await db.commit()
    return {"message": "Alert deleted"}
