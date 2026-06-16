from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models.schedule import ScheduleStatus

class ScheduleCreate(BaseModel):
    dustbin_id: int
    collector_id: int
    scheduled_at: datetime
    notes: Optional[str] = None

class ScheduleUpdate(BaseModel):
    scheduled_at: Optional[datetime] = None
    collector_id: Optional[int] = None
    status: Optional[ScheduleStatus] = None
    notes: Optional[str] = None

class ScheduleResponse(BaseModel):
    id: int
    dustbin_id: int
    collector_id: int
    scheduled_at: datetime
    completed_at: Optional[datetime]
    status: ScheduleStatus
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
