"""
PowerGuard - Electricity Theft Detection System
FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .database import init_db, close_db
from .routers import upload_router, anomaly_router, meters_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown events."""
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


# Create FastAPI application
app = FastAPI(
    title="PowerGuard API",
    description="""
    ## Electricity Theft Detection System
    
    PowerGuard is an ML-powered system for detecting electricity theft and 
    abnormal consumption patterns in smart meter data.
    
    ### Features
    - **Upload** smart meter CSV data
    - **Detect** anomalies using Isolation Forest or Autoencoder
    - **Analyze** consumption patterns with feature engineering
    - **Visualize** results with explainable AI
    
    ### Endpoints
    - `/api/v1/upload` - Data ingestion
    - `/api/v1/anomaly` - Anomaly detection
    - `/api/v1/meters` - Meter data access
    """,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
cors_origins_str = settings.CORS_ORIGINS.strip()
if cors_origins_str == "*":
    # Allow all origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,  # Must be False when using "*"
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    origins = [origin.strip() for origin in cors_origins_str.split(",")]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include routers
app.include_router(upload_router, prefix=settings.API_PREFIX)
app.include_router(anomaly_router, prefix=settings.API_PREFIX)
app.include_router(meters_router, prefix=settings.API_PREFIX)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Check API health status."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "database": "sqlite" if settings.USE_SQLITE else "postgresql"
    }


@app.get("/", tags=["Root"])
async def root():
    """API root - redirect to docs."""
    return {
        "name": "PowerGuard API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }
