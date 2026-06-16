from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from core.database import Base

class ScheduleStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    missed = "missed"

class CollectionSchedule(Base):
    __tablename__ = "collection_schedules"

    id = Column(Integer, primary_key=True, index=True)
    dustbin_id = Column(Integer, ForeignKey("dustbins.id"))
    collector_id = Column(Integer, ForeignKey("users.id"))
    scheduled_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    status = Column(Enum(ScheduleStatus), default=ScheduleStatus.pending)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    dustbin = relationship("Dustbin", back_populates="schedules")
    collector = relationship("User", back_populates="schedules")
