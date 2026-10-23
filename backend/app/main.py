"""EventEase FastAPI application entry point."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import attendees, dashboard, events, health, organizers, payments, registrations, reports, sql_lab, venues
from .config import settings

logger = logging.getLogger("eventease")

DESCRIPTION = """
**EventEase – Event Management System**

REST API for the DBMS mini project: events, venues, organizers, attendees,
registrations and payments are stored in a real MySQL database.

* Interactive documentation: `/docs`
* Health probe: `/api/health`
* The nine DBMS experiments are executed in the SQL Lab (`/api/sql-lab`).
"""


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Optionally create the schema and the demo data when the API starts."""
    if settings.auto_init_db:
        from .db.init_db import init_database

        result = init_database()
        logger.info("Database initialised: %s", result)
    else:
        logger.info(
            "Starting with auto_init_db disabled - run `python backend/scripts/init_db.py` "
            "to create the demo data."
        )
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS is restricted to the local development origin of the Vite frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = settings.api_prefix
app.include_router(health.router, prefix=API_PREFIX)
app.include_router(dashboard.router, prefix=API_PREFIX)
app.include_router(organizers.router, prefix=API_PREFIX)
app.include_router(venues.router, prefix=API_PREFIX)
app.include_router(events.router, prefix=API_PREFIX)
app.include_router(attendees.router, prefix=API_PREFIX)
app.include_router(registrations.router, prefix=API_PREFIX)
app.include_router(payments.router, prefix=API_PREFIX)
app.include_router(reports.router, prefix=API_PREFIX)
app.include_router(sql_lab.router, prefix=API_PREFIX)


@app.get("/", tags=["system"])
def root() -> dict:
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "api_prefix": API_PREFIX,
    }
