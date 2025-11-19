"""
Database configuration and session management
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://aqr_user:aqr_password@localhost:5432/aqr_factors")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Enable connection health checks
    pool_size=10,
    max_overflow=20
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session for FastAPI routes
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database - create all tables
    Only use this for development/testing. In production, use Alembic migrations.
    """
    from backend.models import Base
    Base.metadata.create_all(bind=engine)
