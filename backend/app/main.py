from fastapi import Depends, FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from sqlalchemy import text
from sqlalchemy.orm import Session
import logging

from app.config import settings, parse_cors_origins
from app.database import engine, Base, get_db
from app.seed import seed_database
from app.routers import (
    auth, wearable, academic, training, load_risk,
    scheduler, lifestyle, notifications, rescue,
    insights, privacy, recovery_guide
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("DualWell")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables and seed initial demo data if needed
    logger.info("Initializing DualWell database schema...")
    Base.metadata.create_all(bind=engine)
    if settings.SEED_ON_STARTUP:
        try:
            seed_database()
            logger.info("Database initialization and seed complete.")
        except Exception as e:
            logger.error(f"Seed initialization note: {e}")
    else:
        logger.info("Demo seeding disabled (SEED_ON_STARTUP=false).")
    yield
    # Shutdown
    logger.info("DualWell application shutdown.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="DualWell: Smart Student Wellness and Academic Performance System REST API",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware - exact origins from CORS_ORIGINS (comma-separated env
# var); falls back to localhost origins when unset, so local dev is unchanged.
app.add_middleware(
    CORSMiddleware,
    allow_origins=parse_cors_origins(settings.CORS_ORIGINS),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Safe Global Exception Handler to avoid exposing stack traces (NFR4)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please try again later."}
    )

# Include Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(wearable.router, prefix=settings.API_V1_STR)
app.include_router(academic.router, prefix=settings.API_V1_STR)
app.include_router(training.router, prefix=settings.API_V1_STR)
app.include_router(load_risk.router, prefix=settings.API_V1_STR)
app.include_router(scheduler.router, prefix=settings.API_V1_STR)
app.include_router(lifestyle.router, prefix=settings.API_V1_STR)
app.include_router(notifications.router, prefix=settings.API_V1_STR)
app.include_router(rescue.router, prefix=settings.API_V1_STR)
app.include_router(insights.router, prefix=settings.API_V1_STR)
app.include_router(privacy.router, prefix=settings.API_V1_STR)
app.include_router(recovery_guide.router, prefix=settings.API_V1_STR)

@app.get("/api/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """Readiness probe: runs a real SELECT 1 against the database.

    Returns 200/{"database": "connected"} on success and 503 with
    {"database": "unavailable"} when the database cannot be reached, so
    Render's health checks gate traffic on actual database state.
    """
    try:
        db.execute(text("SELECT 1"))
        database_status = "connected"
        overall = "healthy"
        code = status.HTTP_200_OK
    except Exception as exc:
        logger.error(f"Health check failed - database unreachable: {exc}")
        database_status = "unavailable"
        overall = "degraded"
        code = status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(
        status_code=code,
        content={
            "status": overall,
            "service": "DualWell API",
            "version": settings.VERSION,
            "database": database_status,
        },
    )

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to DualWell API",
        "docs": "/docs",
        "health": "/api/health"
    }
