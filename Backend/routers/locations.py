from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.database import get_db
from models.dustbin import Dustbin
from middleware.role_checker import require_any, require_admin

router = APIRouter(prefix="/locations", tags=["Location Tracking"])

@router.get("/map-data")
async def get_map_data(db: AsyncSession = Depends(get_db), current_user=Depends(require_any)):
    """Returns all bins with coordinates for the map view."""
    result = await db.execute(
        select(Dustbin).where(Dustbin.is_active == True, Dustbin.latitude != None)
    )
    bins = result.scalars().all()

    return [
        {
            "id": b.id,
            "bin_code": b.bin_code,
            "location_name": b.location_name,
            "latitude": b.latitude,
            "longitude": b.longitude,
            "fill_level_percent": b.fill_level_percent,
            "is_full": b.is_full,
            "area": b.area
        }
        for b in bins
    ]

@router.put("/{bin_id}/update-location")
async def update_bin_location(
    bin_id: int,
    latitude: float,
    longitude: float,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin)
):
    result = await db.execute(select(Dustbin).where(Dustbin.id == bin_id))
    dustbin = result.scalar_one_or_none()
    if not dustbin:
        raise HTTPException(status_code=404, detail="Dustbin not found")

    dustbin.latitude = latitude
    dustbin.longitude = longitude
    await db.commit()
    return {"message": f"Location updated for {dustbin.bin_code}"}

@router.get("/areas")
async def get_areas(db: AsyncSession = Depends(get_db), current_user=Depends(require_any)):
    """Returns list of distinct areas."""
    result = await db.execute(select(Dustbin.area).distinct())
    areas = [row[0] for row in result.fetchall() if row[0]]
    return {"areas": areas}
