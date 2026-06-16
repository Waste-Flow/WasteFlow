from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models.alert import AlertType, AlertStatus

class AlertResponse(BaseModel):
    id: int
    dustbin_id: int
    alert_type: AlertType
    status: AlertStatus
    message: str
    fill_level_at_alert: Optional[int]
    sms_sent: bool
    email_sent: bool
    created_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True

class AlertUpdateStatus(BaseModel):
    status: AlertStatus
