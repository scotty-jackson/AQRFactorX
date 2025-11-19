"""
API routes for cross-factor analytics and comparisons
"""
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
import numpy as np
import pandas as pd

from backend.db import get_db
from backend.models import Factor, FactorReturn
from backend import schemas

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/comparison", response_model=schemas.ComparisonResponse)
def compare_factors(
    factor_ids: List[int] = Query(..., description="List of factor IDs to compare"),
    start_date: Optional[date] = Query(None, description="Start date for comparison"),
    end_date: Optional[date] = Query(None, description="End date for comparison"),
    db: Session = Depends(get_db)
):
    """
    Compare multiple factors over a common time period
    """
    if len(factor_ids) < 2:
        raise HTTPException(status_code=400, detail="At least 2 factors required for comparison")

    if len(factor_ids) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 factors allowed for comparison")

    # Verify all factors exist
    factors = db.query(Factor).filter(Factor.id.in_(factor_ids)).all()

    if len(factors) != len(factor_ids):
        raise HTTPException(status_code=404, detail="One or more factors not found")

    # Get returns for all factors
    comparison_data = []

    # Determine common date range if not specified
    if not start_date or not end_date:
        # Find overlapping date range
        for factor in factors:
            if not start_date or (factor.first_date and factor.first_date > start_date):
                start_date = factor.first_date
            if not end_date or (factor.last_date and factor.last_date < end_date):
                end_date = factor.last_date

    for factor in factors:
        # Get returns for this factor
        query = db.query(FactorReturn).filter(FactorReturn.factor_id == factor.id)

        if start_date:
            query = query.filter(FactorReturn.date >= start_date)

        if end_date:
            query = query.filter(FactorReturn.date <= end_date)

        returns = query.order_by(FactorReturn.date).all()

        if not returns:
            continue

        # Calculate cumulative returns
        data_points = []
        cumulative_value = 1.0

        for ret in returns:
            cumulative_value *= (1 + ret.return_value)
            cumulative_return = cumulative_value - 1

            data_points.append(
                schemas.TimeSeriesPoint(
                    date=ret.date,
                    return_value=ret.return_value,
                    cumulative_return=cumulative_return
                )
            )

        comparison_data.append(
            schemas.ComparisonSeriesData(
                factor_id=factor.id,
                factor_code=factor.code,
                factor_name=factor.name,
                data=data_points
            )
        )

    if not comparison_data:
        raise HTTPException(status_code=404, detail="No data found for the specified factors and date range")

    response = schemas.ComparisonResponse(
        start_date=start_date,
        end_date=end_date,
        factors=comparison_data
    )

    return response


@router.get("/correlation", response_model=schemas.CorrelationMatrix)
def compute_correlation_matrix(
    factor_ids: List[int] = Query(..., description="List of factor IDs"),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    db: Session = Depends(get_db)
):
    """
    Compute correlation matrix for selected factors
    """
    if len(factor_ids) < 2:
        raise HTTPException(status_code=400, detail="At least 2 factors required for correlation")

    if len(factor_ids) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 factors allowed for correlation")

    # Verify all factors exist
    factors = db.query(Factor).filter(Factor.id.in_(factor_ids)).all()

    if len(factors) != len(factor_ids):
        raise HTTPException(status_code=404, detail="One or more factors not found")

    # Build a dictionary of factor returns
    factor_returns_dict = {}

    for factor in factors:
        query = db.query(FactorReturn.date, FactorReturn.return_value).filter(
            FactorReturn.factor_id == factor.id
        )

        if start_date:
            query = query.filter(FactorReturn.date >= start_date)

        if end_date:
            query = query.filter(FactorReturn.date <= end_date)

        returns = query.order_by(FactorReturn.date).all()

        if returns:
            factor_returns_dict[factor.code] = pd.Series(
                {ret.date: ret.return_value for ret in returns}
            )

    if len(factor_returns_dict) < 2:
        raise HTTPException(status_code=404, detail="Not enough data for correlation analysis")

    # Create DataFrame with aligned dates
    df = pd.DataFrame(factor_returns_dict)

    # Drop rows with any missing values
    df = df.dropna()

    if len(df) < 10:
        raise HTTPException(
            status_code=400,
            detail="Not enough overlapping observations for correlation (need at least 10)"
        )

    # Compute correlation matrix
    corr_matrix = df.corr()

    # Convert to response format
    factor_codes = corr_matrix.columns.tolist()
    correlations = corr_matrix.values.tolist()

    # Determine actual date range used
    actual_start_date = df.index.min()
    actual_end_date = df.index.max()

    response = schemas.CorrelationMatrix(
        start_date=actual_start_date,
        end_date=actual_end_date,
        factor_codes=factor_codes,
        correlations=correlations
    )

    return response


@router.get("/top-factors", response_model=schemas.TopFactorsResponse)
def get_top_factors(
    period: str = Query("all_time", description="Period: all_time, last_1y, last_3y, last_5y, last_10y"),
    metric: str = Query("annualized_return", description="Metric: annualized_return or sharpe_ratio"),
    limit: int = Query(10, ge=1, le=50, description="Number of top factors to return"),
    region: Optional[str] = Query(None, description="Filter by region"),
    db: Session = Depends(get_db)
):
    """
    Get top performing factors by specified metric and period
    """
    # Determine date range based on period
    end_date = date.today()
    start_date = None

    if period == "last_1y":
        start_date = date(end_date.year - 1, end_date.month, end_date.day)
    elif period == "last_3y":
        start_date = date(end_date.year - 3, end_date.month, end_date.day)
    elif period == "last_5y":
        start_date = date(end_date.year - 5, end_date.month, end_date.day)
    elif period == "last_10y":
        start_date = date(end_date.year - 10, end_date.month, end_date.day)
    elif period != "all_time":
        raise HTTPException(status_code=400, detail="Invalid period specified")

    # Query factors
    query = db.query(Factor)

    if region:
        query = query.filter(Factor.region == region)

    factors = query.all()

    # Compute metrics for each factor over the specified period
    factor_metrics = []

    for factor in factors:
        # Get returns for the period
        returns_query = db.query(FactorReturn).filter(FactorReturn.factor_id == factor.id)

        if start_date:
            returns_query = returns_query.filter(FactorReturn.date >= start_date)

        returns_query = returns_query.filter(FactorReturn.date <= end_date)

        returns = returns_query.order_by(FactorReturn.date).all()

        if not returns or len(returns) < 12:  # Need at least 12 observations
            continue

        # Compute metric
        return_values = np.array([r.return_value for r in returns])
        periods_per_year = 252 if factor.frequency == "Daily" else 12

        if metric == "annualized_return":
            total_return = np.prod(1 + return_values) - 1
            years = len(return_values) / periods_per_year
            metric_value = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        elif metric == "sharpe_ratio":
            mean_return = np.mean(return_values) * periods_per_year
            std_return = np.std(return_values) * np.sqrt(periods_per_year)
            metric_value = mean_return / std_return if std_return > 0 else 0
        else:
            raise HTTPException(status_code=400, detail="Invalid metric. Choose: annualized_return or sharpe_ratio")

        factor_metrics.append({
            'factor_id': factor.id,
            'factor_code': factor.code,
            'factor_name': factor.name,
            'region': factor.region,
            'metric_value': float(metric_value)
        })

    # Sort by metric value (descending) and take top N
    factor_metrics.sort(key=lambda x: x['metric_value'], reverse=True)
    top_factors = factor_metrics[:limit]

    # Add rank
    for i, factor_metric in enumerate(top_factors):
        factor_metric['rank'] = i + 1

    # Convert to response format
    top_factor_objects = [
        schemas.TopFactor(**fm) for fm in top_factors
    ]

    # Determine actual date range
    actual_start_date = start_date if start_date else date(1900, 1, 1)

    response = schemas.TopFactorsResponse(
        period=period,
        metric=metric,
        start_date=actual_start_date,
        end_date=end_date,
        factors=top_factor_objects
    )

    return response


@router.get("/factor-groups", response_model=List[schemas.FactorGroup])
def get_factor_groups(
    db: Session = Depends(get_db)
):
    """
    Get all factor groups
    """
    groups = db.query(Factor.group).filter(Factor.group.isnot(None)).distinct().all()
    return groups
