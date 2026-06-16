from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from core.database import init_db
from services.mqtt_service import start_mqtt_client
from services.scheduler_service import start_scheduler

from routers import (
    auth, dashboard, users, dustbins,
    alerts, schedules, reports, locations,
    settings as settings_router, activity_logs
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Smart Dustbin Backend...")
    await init_db()
    start_mqtt_client()
    start_scheduler()
    yield
    logger.info("Shutting down...")

app = FastAPI(
    title="Smart Dustbin Management System",
    description="Backend API for ultrasonic-based smart dustbin monitoring",
    version="1.0.0",
    lifespan=lifespan
)

# CORS — allow React frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(users.router)
app.include_router(dustbins.router)
app.include_router(alerts.router)
app.include_router(schedules.router)
app.include_router(reports.router)
app.include_router(locations.router)
app.include_router(settings_router.router)
app.include_router(activity_logs.router)

@app.get("/")
def root():
    return {"message": "Smart Dustbin System API is running", "docs": "/docs"}
