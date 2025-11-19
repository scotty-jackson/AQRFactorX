"""
FastAPI main application for AQR Factor Explorer
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api import factors, analytics

# Create FastAPI app
app = FastAPI(
    title="AQR Factor Explorer API",
    description="API for exploring AQR factor performance data",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
# In production, restrict this to your frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(factors.router)
app.include_router(analytics.router)


@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "AQR Factor Explorer API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }


@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AQR Factor Explorer API"
    }


@app.get("/api/regions")
def get_regions():
    """Get list of available regions"""
    return {
        "regions": [
            "US",
            "Global",
            "International",
            "Europe",
            "Japan",
            "Asia Pacific",
            "Emerging Markets",
            "Developed ex US"
        ]
    }


@app.get("/api/asset-classes")
def get_asset_classes():
    """Get list of available asset classes"""
    return {
        "asset_classes": [
            "Equity",
            "Multi-Asset",
            "Fixed Income",
            "FX",
            "Commodities"
        ]
    }


@app.get("/api/frequencies")
def get_frequencies():
    """Get list of available frequencies"""
    return {
        "frequencies": [
            "Daily",
            "Monthly"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)
