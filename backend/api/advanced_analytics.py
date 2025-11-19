"""
Advanced analytics API routes: regression analysis, portfolio optimization, attribution
"""
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from scipy.optimize import minimize

from backend.db import get_db
from backend.models import Factor, FactorReturn
from backend import schemas
from pydantic import BaseModel

router = APIRouter(prefix="/api/advanced", tags=["advanced-analytics"])


# Response models
class RegressionResult(BaseModel):
    dependent_factor_code: str
    independent_factor_codes: List[str]
    coefficients: List[float]
    intercept: float
    r_squared: float
    adjusted_r_squared: float
    residual_volatility: float
    observations: int


class PortfolioWeights(BaseModel):
    factor_id: int
    factor_code: str
    weight: float


class PortfolioOptimizationResult(BaseModel):
    weights: List[PortfolioWeights]
    expected_return: float
    expected_volatility: float
    sharpe_ratio: float
    optimization_method: str


class AttributionResult(BaseModel):
    factor_id: int
    factor_code: str
    contribution: float
    percentage_contribution: float


class PerformanceAttributionResponse(BaseModel):
    portfolio_return: float
    attributions: List[AttributionResult]


@router.post("/regression", response_model=RegressionResult)
def factor_regression(
    dependent_factor_id: int = Query(..., description="Dependent variable factor ID"),
    independent_factor_ids: List[int] = Query(..., description="Independent variable factor IDs"),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    db: Session = Depends(get_db)
):
    """
    Perform multi-factor regression analysis

    Regresses one factor (Y) against multiple other factors (X1, X2, ...)
    Returns coefficients, R-squared, and other regression statistics
    """
    # Get dependent factor
    dep_factor = db.query(Factor).filter(Factor.id == dependent_factor_id).first()
    if not dep_factor:
        raise HTTPException(status_code=404, detail="Dependent factor not found")

    # Get independent factors
    indep_factors = db.query(Factor).filter(Factor.id.in_(independent_factor_ids)).all()
    if len(indep_factors) != len(independent_factor_ids):
        raise HTTPException(status_code=404, detail="One or more independent factors not found")

    # Build dataframe with all returns
    data_dict = {}

    # Get dependent variable returns
    dep_query = db.query(FactorReturn.date, FactorReturn.return_value).filter(
        FactorReturn.factor_id == dependent_factor_id
    )
    if start_date:
        dep_query = dep_query.filter(FactorReturn.date >= start_date)
    if end_date:
        dep_query = dep_query.filter(FactorReturn.date <= end_date)

    dep_returns = dep_query.all()
    data_dict['Y'] = pd.Series({r.date: r.return_value for r in dep_returns})

    # Get independent variable returns
    for factor in indep_factors:
        indep_query = db.query(FactorReturn.date, FactorReturn.return_value).filter(
            FactorReturn.factor_id == factor.id
        )
        if start_date:
            indep_query = indep_query.filter(FactorReturn.date >= start_date)
        if end_date:
            indep_query = indep_query.filter(FactorReturn.date <= end_date)

        indep_returns = indep_query.all()
        data_dict[factor.code] = pd.Series({r.date: r.return_value for r in indep_returns})

    # Create aligned dataframe
    df = pd.DataFrame(data_dict)
    df = df.dropna()

    if len(df) < 10:
        raise HTTPException(
            status_code=400,
            detail="Not enough observations for regression (need at least 10)"
        )

    # Perform regression
    X = df[[f.code for f in indep_factors]].values
    y = df['Y'].values

    model = LinearRegression()
    model.fit(X, y)

    # Calculate statistics
    y_pred = model.predict(X)
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)

    n = len(y)
    p = X.shape[1]
    adjusted_r_squared = 1 - (1 - r_squared) * (n - 1) / (n - p - 1)

    residuals = y - y_pred
    residual_vol = np.std(residuals)

    return RegressionResult(
        dependent_factor_code=dep_factor.code,
        independent_factor_codes=[f.code for f in indep_factors],
        coefficients=model.coef_.tolist(),
        intercept=float(model.intercept_),
        r_squared=float(r_squared),
        adjusted_r_squared=float(adjusted_r_squared),
        residual_volatility=float(residual_vol),
        observations=int(n)
    )


@router.post("/portfolio-optimization", response_model=PortfolioOptimizationResult)
def optimize_portfolio(
    factor_ids: List[int] = Query(..., description="Factor IDs to include in portfolio"),
    method: str = Query("sharpe", description="Optimization method: sharpe, min_vol, max_return"),
    target_return: Optional[float] = Query(None, description="Target return for min_vol optimization"),
    start_date: Optional[date] = Query(None, description="Start date for historical data"),
    end_date: Optional[date] = Query(None, description="End date for historical data"),
    db: Session = Depends(get_db)
):
    """
    Optimize portfolio weights for a set of factors

    Methods:
    - sharpe: Maximize Sharpe ratio
    - min_vol: Minimize volatility (optionally subject to target return)
    - max_return: Maximize return subject to volatility constraint
    """
    if len(factor_ids) < 2:
        raise HTTPException(status_code=400, detail="At least 2 factors required")

    # Get factors
    factors = db.query(Factor).filter(Factor.id.in_(factor_ids)).all()
    if len(factors) != len(factor_ids):
        raise HTTPException(status_code=404, detail="One or more factors not found")

    # Build returns dataframe
    returns_dict = {}
    for factor in factors:
        query = db.query(FactorReturn.date, FactorReturn.return_value).filter(
            FactorReturn.factor_id == factor.id
        )
        if start_date:
            query = query.filter(FactorReturn.date >= start_date)
        if end_date:
            query = query.filter(FactorReturn.date <= end_date)

        returns = query.all()
        returns_dict[factor.id] = pd.Series({r.date: r.return_value for r in returns})

    df = pd.DataFrame(returns_dict)
    df = df.dropna()

    if len(df) < 12:
        raise HTTPException(
            status_code=400,
            detail="Not enough observations for optimization (need at least 12)"
        )

    # Calculate expected returns and covariance
    returns = df.values
    mean_returns = np.mean(returns, axis=0)
    cov_matrix = np.cov(returns.T)

    # Annualize (assuming monthly data)
    annual_returns = mean_returns * 12
    annual_cov = cov_matrix * 12

    n_assets = len(factors)

    # Optimization objective functions
    def portfolio_return(weights):
        return np.dot(weights, annual_returns)

    def portfolio_volatility(weights):
        return np.sqrt(np.dot(weights.T, np.dot(annual_cov, weights)))

    def negative_sharpe(weights):
        ret = portfolio_return(weights)
        vol = portfolio_volatility(weights)
        return -ret / vol if vol > 0 else 0

    # Constraints
    constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]  # Weights sum to 1

    if method == "min_vol" and target_return is not None:
        constraints.append({
            'type': 'eq',
            'fun': lambda w: portfolio_return(w) - target_return
        })

    # Bounds: all weights between 0 and 1 (long-only)
    bounds = tuple((0, 1) for _ in range(n_assets))

    # Initial guess: equal weights
    initial_weights = np.array([1.0 / n_assets] * n_assets)

    # Optimize
    if method == "sharpe":
        result = minimize(negative_sharpe, initial_weights, method='SLSQP',
                         bounds=bounds, constraints=constraints)
    elif method == "min_vol":
        result = minimize(portfolio_volatility, initial_weights, method='SLSQP',
                         bounds=bounds, constraints=constraints)
    elif method == "max_return":
        result = minimize(lambda w: -portfolio_return(w), initial_weights,
                         method='SLSQP', bounds=bounds, constraints=constraints)
    else:
        raise HTTPException(status_code=400, detail="Invalid optimization method")

    if not result.success:
        raise HTTPException(status_code=500, detail="Optimization failed")

    optimal_weights = result.x
    optimal_return = portfolio_return(optimal_weights)
    optimal_vol = portfolio_volatility(optimal_weights)
    optimal_sharpe = optimal_return / optimal_vol if optimal_vol > 0 else 0

    weights_list = [
        PortfolioWeights(
            factor_id=factors[i].id,
            factor_code=factors[i].code,
            weight=float(optimal_weights[i])
        )
        for i in range(n_assets)
    ]

    return PortfolioOptimizationResult(
        weights=weights_list,
        expected_return=float(optimal_return),
        expected_volatility=float(optimal_vol),
        sharpe_ratio=float(optimal_sharpe),
        optimization_method=method
    )


@router.post("/performance-attribution", response_model=PerformanceAttributionResponse)
def performance_attribution(
    portfolio_weights: List[dict] = Query(..., description="List of {factor_id: int, weight: float}"),
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    db: Session = Depends(get_db)
):
    """
    Attribute portfolio performance to individual factors

    Shows how much each factor contributed to total portfolio return
    """
    # Parse weights
    weights_dict = {w['factor_id']: w['weight'] for w in portfolio_weights}
    factor_ids = list(weights_dict.keys())

    # Get factors
    factors = db.query(Factor).filter(Factor.id.in_(factor_ids)).all()
    if len(factors) != len(factor_ids):
        raise HTTPException(status_code=404, detail="One or more factors not found")

    # Get returns
    returns_dict = {}
    for factor in factors:
        query = db.query(FactorReturn.date, FactorReturn.return_value).filter(
            FactorReturn.factor_id == factor.id,
            FactorReturn.date >= start_date,
            FactorReturn.date <= end_date
        )
        returns = query.all()
        returns_dict[factor.id] = pd.Series({r.date: r.return_value for r in returns})

    df = pd.DataFrame(returns_dict)
    df = df.dropna()

    if df.empty:
        raise HTTPException(status_code=404, detail="No data found for specified period")

    # Calculate factor contributions
    contributions = []
    total_portfolio_return = 0

    for factor in factors:
        weight = weights_dict[factor.id]
        factor_return = (1 + df[factor.id]).prod() - 1
        contribution = weight * factor_return
        total_portfolio_return += contribution

        contributions.append(
            AttributionResult(
                factor_id=factor.id,
                factor_code=factor.code,
                contribution=float(contribution),
                percentage_contribution=0  # Will calculate after total is known
            )
        )

    # Calculate percentage contributions
    if total_portfolio_return != 0:
        for attr in contributions:
            attr.percentage_contribution = (attr.contribution / total_portfolio_return) * 100

    return PerformanceAttributionResponse(
        portfolio_return=float(total_portfolio_return),
        attributions=contributions
    )
