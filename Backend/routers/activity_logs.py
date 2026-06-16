from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from core.database import get_db
from models.activity_log import ActivityLog
from models.user import User, UserRole
from middleware.role_checker import require_admin, require_any

router = APIRouter(prefix="/activity-logs", tags=["Activity Logs"])

@router.get("/")
async def get_activity_logs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_any),
    limit: int = 50
):
    query = select(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(limit)

    # Collectors see only their own logs
    if current_user.role == UserRole.collector:
        query = query.where(ActivityLog.user_id == current_user.id)

    result = await db.execute(query)
    logs = result.scalars().all()

    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "module": log.module,
            "ip_address": log.ip_address,
            "created_at": log.created_at.isoformat()
        }
        for log in logs
    ]

async def log_activity(db: AsyncSession, user_id: int, action: str, module: str, ip: str = None):
    """Helper to log an activity from any router."""
    log = ActivityLog(user_id=user_id, action=action, module=module, ip_address=ip)
    db.add(log)
    await db.commit()
