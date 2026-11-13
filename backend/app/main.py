"""Application entry point. Run with: uvicorn app.main:app --port 8000"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.alerts.router import router as alerts_router
from app.core import health
from app.core.config import get_settings
from app.core.errors import register_error_handlers
from app.dashboard.router import router as dashboard_router
from app.feedback.router import router as feedback_router
from app.sms.router import router as sms_router

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

app = FastAPI(title="Company X Feedback API", version="1.0.0")

# Browsers only let the Next.js site call this API if we explicitly allow its origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_error_handlers(app)

for router in (health.router, feedback_router, dashboard_router, alerts_router, sms_router):
    app.include_router(router)
