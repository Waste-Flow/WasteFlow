from fastapi import APIRouter, Depends
from pydantic import BaseModel
from core.config import settings
from middleware.role_checker import require_admin

router = APIRouter(prefix="/settings", tags=["Settings"])

class ThresholdUpdate(BaseModel):
    fill_level_threshold: int

@router.get("/")
async def get_settings(current_user=Depends(require_admin)):
    return {
        "app_name": settings.APP_NAME,
        "fill_level_threshold": settings.FILL_LEVEL_THRESHOLD,
        "mqtt_broker": settings.MQTT_BROKER,
        "mqtt_port": settings.MQTT_PORT,
        "alert_sms_enabled": bool(settings.TWILIO_ACCOUNT_SID),
        "alert_email_enabled": bool(settings.SMTP_USER)
    }

@router.put("/threshold")
async def update_threshold(data: ThresholdUpdate, current_user=Depends(require_admin)):
    """Update the fill level alert threshold (requires app restart to fully apply)."""
    settings.FILL_LEVEL_THRESHOLD = data.fill_level_threshold
    return {"message": f"Threshold updated to {data.fill_level_threshold}%"}
