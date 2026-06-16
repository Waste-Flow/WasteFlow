from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DustbinCreate(BaseModel):
    bin_code: str
    location_name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    bin_height_cm: float = 100.0
    area: Optional[str] = None

class DustbinUpdate(BaseModel):
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    bin_height_cm: Optional[float] = None
    area: Optional[str] = None
    is_active: Optional[bool] = None

class SensorDataInput(BaseModel):
    bin_code: str
    distance_cm: float                  # Raw distance reading from HC-SR04

class DustbinResponse(BaseModel):
    id: int
    bin_code: str
    location_name: str
    latitude: Optional[float]
    longitude: Optional[float]
    bin_height_cm: float
    fill_level_percent: float
    is_full: bool
    is_active: bool
    area: Optional[str]
    last_collected_at: Optional[datetime]
    last_updated_at: datetime

    class Config:
        from_attributes = True

class FillHistoryResponse(BaseModel):
    id: int
    dustbin_id: int
    fill_level_percent: float
    distance_cm: float
    recorded_at: datetime

    class Config:
        from_attributes = True
