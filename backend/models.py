"""
SQLAlchemy database models for AQR Factor Explorer
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class FactorGroup(Base):
    """Factor group/category (Value, Momentum, Quality, etc.)"""
    __tablename__ = "factor_group"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    factors = relationship("Factor", back_populates="group")


class Factor(Base):
    """Factor metadata and descriptive information"""
    __tablename__ = "factor"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    provider = Column(String(100), default="AQR", nullable=False)
    region = Column(String(100), index=True)  # US, Global, Dev ex US, EM, etc.
    asset_class = Column(String(100), index=True)  # Equity, Multi-Asset, FX, etc.
    frequency = Column(String(50), index=True)  # Daily, Monthly
    description = Column(Text)
    first_date = Column(Date)
    last_date = Column(Date)
    group_id = Column(Integer, ForeignKey("factor_group.id"), index=True)

    # Cached statistics (updated during ETL)
    total_return = Column(Float)
    annualized_return = Column(Float)
    annualized_volatility = Column(Float)
    max_drawdown = Column(Float)
    sharpe_ratio = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    returns = relationship("FactorReturn", back_populates="factor", cascade="all, delete-orphan")
    group = relationship("FactorGroup", back_populates="factors")

    # Indexes for common queries
    __table_args__ = (
        Index('idx_factor_region_freq', 'region', 'frequency'),
    )


class FactorReturn(Base):
    """Time series of factor returns"""
    __tablename__ = "factor_return"

    id = Column(Integer, primary_key=True, index=True)
    factor_id = Column(Integer, ForeignKey("factor.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    return_value = Column(Float, nullable=False)  # Returns in decimal form (e.g., 0.05 = 5%)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    factor = relationship("Factor", back_populates="returns")

    # Composite unique constraint and indexes
    __table_args__ = (
        Index('idx_factor_return_factor_date', 'factor_id', 'date', unique=True),
        Index('idx_factor_return_date', 'date'),
    )
