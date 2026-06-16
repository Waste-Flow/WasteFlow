from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from core.database import Base

class AlertType(str, enum.Enum):
    bin_full = "bin_full"
    bin_overflow = "bin_overflow"
    sensor_offline = "sensor_offline"
    collection_overdue = "collection_overdue"

class AlertStatus(str, enum.Enum):
    pending = "pending"
    acknowledged = "acknowledged"
    resolved = "resolved"

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    dustbin_id = Column(Integer, ForeignKey("dustbins.id"))
    alert_type = Column(Enum(AlertType), default=AlertType.bin_full)
    status = Column(Enum(AlertStatus), default=AlertStatus.pending)
    message = Column(String, nullable=False)
    fill_level_at_alert = Column(Integer, nullable=True)
    sms_sent = Column(Boolean, default=False)
    email_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    dustbin = relationship("Dustbin", back_populates="alerts")
