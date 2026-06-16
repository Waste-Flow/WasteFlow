from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from io import BytesIO
import pandas as pd
from datetime import date, timedelta
from core.database import get_db
from models.dustbin import Dustbin, FillLevelHistory
from models.alert import Alert
from models.schedule import CollectionSchedule, ScheduleStatus
from middleware.role_checker import require_admin_or_supervisor

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/summary")
async def get_summary_report(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin_or_supervisor)
):
    """Returns JSON summary report."""
    bins = await db.execute(select(Dustbin).where(Dustbin.is_active == True))
    bins = bins.scalars().all()

    total = len(bins)
    full = sum(1 for b in bins if b.is_full)
    avg_fill = round(sum(b.fill_level_percent for b in bins) / total, 2) if total else 0

    alerts = await db.execute(select(func.count(Alert.id)))
    total_alerts = alerts.scalar()

    completed = await db.execute(
        select(func.count(CollectionSchedule.id)).where(CollectionSchedule.status == ScheduleStatus.completed)
    )
    completed_collections = completed.scalar()

    return {
        "total_bins": total,
        "full_bins": full,
        "average_fill_level_percent": avg_fill,
        "total_alerts_raised": total_alerts,
        "completed_collections": completed_collections,
        "report_date": date.today().isoformat()
    }

@router.get("/export/excel")
async def export_excel_report(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin_or_supervisor)
):
    """Exports all dustbin status as Excel file."""
    result = await db.execute(select(Dustbin))
    bins = result.scalars().all()

    data = [
        {
            "Bin Code": b.bin_code,
            "Location": b.location_name,
            "Area": b.area,
            "Fill Level (%)": b.fill_level_percent,
            "Is Full": b.is_full,
            "Last Collected": b.last_collected_at,
            "Last Updated": b.last_updated_at
        }
        for b in bins
    ]

    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Dustbin Report")
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=dustbin_report.xlsx"}
    )

@router.get("/fill-history/{bin_id}")
async def get_bin_fill_history_report(
    bin_id: int,
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin_or_supervisor)
):
    """Fill level history for a specific bin over N days."""
    since = date.today() - timedelta(days=days)
    result = await db.execute(
        select(FillLevelHistory)
        .where(FillLevelHistory.dustbin_id == bin_id)
        .where(FillLevelHistory.recorded_at >= since)
        .order_by(FillLevelHistory.recorded_at)
    )
    records = result.scalars().all()

    return [
        {
            "recorded_at": r.recorded_at.isoformat(),
            "fill_level_percent": r.fill_level_percent,
            "distance_cm": r.distance_cm
        }
        for r in records
    ]
