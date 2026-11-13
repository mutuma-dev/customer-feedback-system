"""Application entry point (Spring: the @SpringBootApplication class).

Start it with:  uvicorn app.main:app --reload --port 8000
  "app.main:app" means: in the file app/main.py, use the object called `app`.
"""

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

# Make INFO messages (like "SMS not configured; would send ...") visible in the terminal.
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

app = FastAPI(title="Company X Feedback API", version="1.0.0")

# CORS: browsers refuse to let a website on port 3000 call an API on port 8000 unless the
# API says "this website is allowed". These are the allowed websites (from .env).
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_error_handlers(app)

# Plug in every group of endpoints.
for router in (health.router, feedback_router, dashboard_router, alerts_router, sms_router):
    app.include_router(router)
