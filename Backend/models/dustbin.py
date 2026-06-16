from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base

class Dustbin(Base):
    __tablename__ = "dustbins"

    id = Column(Integer, primary_key=True, index=True)
    bin_code = Column(String, unique=True, nullable=False)       # e.g. BIN-001
    location_name = Column(String, nullable=False)               # e.g. Market Street
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    bin_height_cm = Column(Float, default=100.0)                 # Total height in cm
    current_distance_cm = Column(Float, default=100.0)           # Distance from sensor to waste
    fill_level_percent = Column(Float, default=0.0)              # Calculated fill %
    is_full = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    area = Column(String, nullable=True)
    last_collected_at = Column(DateTime, nullable=True)
    last_updated_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    alerts = relationship("Alert", back_populates="dustbin")
    schedules = relationship("CollectionSchedule", back_populates="dustbin")


class FillLevelHistory(Base):
    __tablename__ = "fill_level_history"

    id = Column(Integer, primary_key=True, index=True)
    dustbin_id = Column(Integer, ForeignKey("dustbins.id"))
    fill_level_percent = Column(Float)
    distance_cm = Column(Float)
    recorded_at = Column(DateTime, default=datetime.utcnow)
