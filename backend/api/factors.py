"""
API routes for factor data and statistics
"""
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import numpy as np
import pandas as pd

from backend.db import get_db
from backend.models import Factor, FactorReturn, FactorGroup
from backend import schemas

router = APIRouter(prefix="/api/factors", tags=["factors"])


@router.get("", response_model=List[schemas.FactorSummary])
def list_factors(
    region: Optional[str] = Query(None, description="Filter by region"),
    asset_class: Optional[str] = Query(None, description="Filter by asset class"),
    frequency: Optional[str] = Query(None, description="Filter by frequency"),
    group_id: Optional[int] = Query(None, description="Filter by factor group"),
    search: Optional[str] = Query(None, description="Search by name or code"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db)
):
    """
    List all factors with optional filtering
    """
    query = db.query(Factor)

    # Apply filters
    if region:
        query = query.filter(Factor.region == region)

    if asset_class:
        query = query.filter(Factor.asset_class == asset_class)

    if frequency:
        query = query.filter(Factor.frequency == frequency)

    if group_id:
        query = query.filter(Factor.group_id == group_id)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Factor.name.ilike(search_term),
                Factor.code.ilike(search_term)
            )
        )

    # Order by name
    query = query.order_by(Factor.name)

    # Apply pagination
    factors = query.offset(offset).limit(limit).all()

    return factors


@router.get("/{factor_id}", response_model=schemas.FactorDetail)
def get_factor(
    factor_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific factor
    """
    factor = db.query(Factor).filter(Factor.id == factor_id).first()

    if not factor:
        raise HTTPException(status_code=404, detail="Factor not found")

    return factor


@router.get("/{factor_id}/timeseries", response_model=schemas.TimeSeriesResponse)
def get_factor_timeseries(
    factor_id: int,
    start_date: Optional[date] = Query(None, description="Start date for time series"),
    end_date: Optional[date] = Query(None, description="End date for time series"),
    cumulative: bool = Query(True, description="Include cumulative returns"),
    db: Session = Depends(get_db)
):
    """
    Get time series data for a factor
    """
    # Check if factor exists
    factor = db.query(Factor).filter(Factor.id == factor_id).first()
    if not factor:
        raise HTTPException(status_code=404, detail="Factor not found")

    # Build query for returns
    query = db.query(FactorReturn).filter(FactorReturn.factor_id == factor_id)

    if start_date:
        query = query.filter(FactorReturn.date >= start_date)

    if end_date:
        query = query.filter(FactorReturn.date <= end_date)

    # Order by date
    returns = query.order_by(FactorReturn.date).all()

    if not returns:
        raise HTTPException(status_code=404, detail="No return data found for this factor")

    # Convert to response format
    data_points = []
    cumulative_value = 1.0

    for ret in returns:
        if cumulative:
            cumulative_value *= (1 + ret.return_value)
            cumulative_return = cumulative_value - 1
        else:
            cumulative_return = None

        data_points.append(
            schemas.TimeSeriesPoint(
                date=ret.date,
                return_value=ret.return_value,
                cumulative_return=cumulative_return
            )
        )

    response = schemas.TimeSeriesResponse(
        factor_id=factor.id,
        factor_code=factor.code,
        factor_name=factor.name,
        start_date=returns[0].date,
        end_date=returns[-1].date,
        data=data_points
    )

    return response


@router.get("/{factor_id}/rolling", response_model=schemas.RollingStatsResponse)
def get_rolling_statistics(
    factor_id: int,
    window_length: int = Query(36, ge=1, le=120, description="Rolling window length in periods"),
    metric: str = Query("return", description="Metric to compute: return, volatility, sharpe"),
    db: Session = Depends(get_db)
):
    """
    Get rolling statistics for a factor
    """
    # Check if factor exists
    factor = db.query(Factor).filter(Factor.id == factor_id).first()
    if not factor:
        raise HTTPException(status_code=404, detail="Factor not found")

    # Get all returns
    returns = db.query(FactorReturn).filter(
        FactorReturn.factor_id == factor_id
    ).order_by(FactorReturn.date).all()

    if len(returns) < window_length:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough data. Need at least {window_length} observations."
        )

    # Convert to pandas Series for rolling calculations
    dates = [r.date for r in returns]
    values = [r.return_value for r in returns]
    series = pd.Series(values, index=dates)

    # Compute rolling metric
    if metric == "return":
        # Annualized rolling return
        periods_per_year = 252 if factor.frequency == "Daily" else 12
        rolling_values = series.rolling(window=window_length).apply(
            lambda x: ((1 + x).prod() ** (periods_per_year / len(x)) - 1) if len(x) > 0 else np.nan
        )
    elif metric == "volatility":
        # Annualized rolling volatility
        periods_per_year = 252 if factor.frequency == "Daily" else 12
        rolling_values = series.rolling(window=window_length).std() * np.sqrt(periods_per_year)
    elif metric == "sharpe":
        # Rolling Sharpe ratio (assuming 0 risk-free rate)
        periods_per_year = 252 if factor.frequency == "Daily" else 12
        rolling_mean = series.rolling(window=window_length).mean() * periods_per_year
        rolling_std = series.rolling(window=window_length).std() * np.sqrt(periods_per_year)
        rolling_values = rolling_mean / rolling_std
    else:
        raise HTTPException(status_code=400, detail="Invalid metric. Choose: return, volatility, or sharpe")

    # Convert to response format
    data_points = []
    for date_val, value in rolling_values.items():
        if not pd.isna(value):
            data_points.append(
                schemas.RollingStatPoint(
                    date=date_val,
                    value=float(value)
                )
            )

    response = schemas.RollingStatsResponse(
        factor_id=factor.id,
        factor_code=factor.code,
        metric=metric,
        window_length=window_length,
        data=data_points
    )

    return response


@router.get("/{factor_id}/statistics", response_model=schemas.FactorStatistics)
def get_factor_statistics(
    factor_id: int,
    start_date: Optional[date] = Query(None, description="Start date for statistics"),
    end_date: Optional[date] = Query(None, description="End date for statistics"),
    db: Session = Depends(get_db)
):
    """
    Compute statistics for a factor over a specific period
    """
    # Check if factor exists
    factor = db.query(Factor).filter(Factor.id == factor_id).first()
    if not factor:
        raise HTTPException(status_code=404, detail="Factor not found")

    # Get returns for the period
    query = db.query(FactorReturn).filter(FactorReturn.factor_id == factor_id)

    if start_date:
        query = query.filter(FactorReturn.date >= start_date)
    else:
        start_date = factor.first_date

    if end_date:
        query = query.filter(FactorReturn.date <= end_date)
    else:
        end_date = factor.last_date

    returns = query.order_by(FactorReturn.date).all()

    if not returns:
        raise HTTPException(status_code=404, detail="No return data found for this period")

    # Convert to numpy array for calculations
    return_values = np.array([r.return_value for r in returns])

    # Periods per year
    periods_per_year = 252 if factor.frequency == "Daily" else 12

    # Total return
    total_return = np.prod(1 + return_values) - 1

    # Annualized return
    n_periods = len(return_values)
    years = n_periods / periods_per_year
    annualized_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0

    # Annualized volatility
    annualized_volatility = np.std(return_values) * np.sqrt(periods_per_year)

    # Sharpe ratio
    sharpe_ratio = annualized_return / annualized_volatility if annualized_volatility > 0 else 0

    # Max drawdown
    cumulative = np.cumprod(1 + return_values)
    running_max = np.maximum.accumulate(cumulative)
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = np.min(drawdown)

    # Best and worst months
    best_month = float(np.max(return_values))
    worst_month = float(np.min(return_values))

    # Positive months
    positive_months = int(np.sum(return_values > 0))
    total_months = len(return_values)

    response = schemas.FactorStatistics(
        factor_id=factor.id,
        factor_code=factor.code,
        start_date=start_date,
        end_date=end_date,
        total_return=float(total_return),
        annualized_return=float(annualized_return),
        annualized_volatility=float(annualized_volatility),
        sharpe_ratio=float(sharpe_ratio),
        max_drawdown=float(max_drawdown),
        best_month=best_month,
        worst_month=worst_month,
        positive_months=positive_months,
        total_months=total_months
    )

    return response
