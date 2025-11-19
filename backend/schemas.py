"""
Pydantic schemas for request and response validation
"""
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# Factor Group Schemas
class FactorGroupBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None


class FactorGroup(FactorGroupBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Factor Schemas
class FactorBase(BaseModel):
    code: str
    name: str
    provider: str = "AQR"
    region: Optional[str] = None
    asset_class: Optional[str] = None
    frequency: Optional[str] = None
    description: Optional[str] = None


class FactorSummary(FactorBase):
    """Summary info for factor listing"""
    id: int
    first_date: Optional[date] = None
    last_date: Optional[date] = None
    annualized_return: Optional[float] = None
    annualized_volatility: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    group_id: Optional[int] = None

    class Config:
        from_attributes = True


class FactorDetail(FactorSummary):
    """Detailed factor info including all cached statistics"""
    total_return: Optional[float] = None
    max_drawdown: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    group: Optional[FactorGroup] = None

    class Config:
        from_attributes = True


# Factor Return Schemas
class FactorReturnBase(BaseModel):
    date: date
    return_value: float


class FactorReturn(FactorReturnBase):
    id: int
    factor_id: int

    class Config:
        from_attributes = True


# Time Series Response
class TimeSeriesPoint(BaseModel):
    date: date
    return_value: float
    cumulative_return: Optional[float] = None


class TimeSeriesResponse(BaseModel):
    factor_id: int
    factor_code: str
    factor_name: str
    start_date: date
    end_date: date
    data: List[TimeSeriesPoint]


# Comparison Response
class ComparisonSeriesData(BaseModel):
    factor_id: int
    factor_code: str
    factor_name: str
    data: List[TimeSeriesPoint]


class ComparisonResponse(BaseModel):
    start_date: date
    end_date: date
    factors: List[ComparisonSeriesData]


# Rolling Statistics Response
class RollingStatPoint(BaseModel):
    date: date
    value: float


class RollingStatsResponse(BaseModel):
    factor_id: int
    factor_code: str
    metric: str
    window_length: int
    data: List[RollingStatPoint]


# Correlation Matrix Response
class CorrelationPair(BaseModel):
    factor1_code: str
    factor2_code: str
    correlation: float


class CorrelationMatrix(BaseModel):
    start_date: date
    end_date: date
    factor_codes: List[str]
    correlations: List[List[float]]


# Top Factors Response
class TopFactor(BaseModel):
    factor_id: int
    factor_code: str
    factor_name: str
    region: Optional[str]
    metric_value: float
    rank: int


class TopFactorsResponse(BaseModel):
    period: str
    metric: str
    start_date: date
    end_date: date
    factors: List[TopFactor]


# Statistics Summary
class FactorStatistics(BaseModel):
    """Computed statistics for a factor over a specific period"""
    factor_id: int
    factor_code: str
    start_date: date
    end_date: date
    total_return: float
    annualized_return: float
    annualized_volatility: float
    sharpe_ratio: float
    max_drawdown: float
    best_month: Optional[float] = None
    worst_month: Optional[float] = None
    positive_months: Optional[int] = None
    total_months: Optional[int] = None


# Query Parameters
class FactorQueryParams(BaseModel):
    region: Optional[str] = None
    asset_class: Optional[str] = None
    frequency: Optional[str] = None
    group_id: Optional[int] = None
    search: Optional[str] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class TimeSeriesQueryParams(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    cumulative: bool = True


class ComparisonQueryParams(BaseModel):
    factor_ids: List[int]
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class RollingQueryParams(BaseModel):
    window_length: int = Field(default=36, ge=1, le=120)  # in months by default
    metric: str = Field(default="return")  # return, volatility, sharpe


class CorrelationQueryParams(BaseModel):
    factor_ids: List[int]
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    frequency: str = "monthly"
