"""
Monitoring and health check endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import redis
import os

from backend.db import get_db

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])


@router.get("/health/detailed")
def detailed_health_check(db: Session = Depends(get_db)):
    """Comprehensive health check"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }

    # Database check
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {"status": "healthy"}
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }

    # Redis check
    try:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        r = redis.from_url(redis_url)
        r.ping()
        health_status["checks"]["redis"] = {"status": "healthy"}
    except Exception as e:
        health_status["checks"]["redis"] = {
            "status": "degraded",
            "error": str(e),
            "note": "Caching disabled"
        }

    return health_status


@router.get("/stats")
def get_system_stats(db: Session = Depends(get_db)):
    """Get system statistics"""
    from backend.models import Factor, FactorReturn

    # Count factors
    factor_count = db.query(Factor).count()

    # Count returns
    return_count = db.query(FactorReturn).count()

    # Get date ranges
    from sqlalchemy import func
    date_range = db.query(
        func.min(FactorReturn.date).label('first_date'),
        func.max(FactorReturn.date).label('last_date')
    ).first()

    # Count by region
    region_counts = db.query(
        Factor.region,
        func.count(Factor.id).label('count')
    ).group_by(Factor.region).all()

    return {
        "factors": {
            "total": factor_count,
            "by_region": {r.region: r.count for r in region_counts if r.region}
        },
        "returns": {
            "total_observations": return_count,
            "date_range": {
                "first": date_range.first_date if date_range else None,
                "last": date_range.last_date if date_range else None
            }
        }
    }


@router.get("/version")
def get_version():
    """Get API version information"""
    return {
        "version": "1.0.0",
        "api_name": "AQR Factor Explorer API",
        "python_version": "3.11+",
        "features": [
            "Factor data ingestion",
            "Time series analysis",
            "Cross-factor comparisons",
            "Portfolio optimization",
            "Performance attribution",
            "Data export (CSV/Excel)",
            "Caching with Redis"
        ]
    }
