# AQR Factor Explorer API Documentation

Complete API reference for the AQR Factor Explorer backend.

**Base URL**: `http://localhost:8000`
**API Documentation**: `http://localhost:8000/api/docs` (Swagger UI)
**Alternative Docs**: `http://localhost:8000/api/redoc` (ReDoc)

---

## Authentication

Currently, the API is public and does not require authentication. For production deployment, implement authentication middleware.

---

## Core Endpoints

### Factor Management

#### List All Factors
```http
GET /api/factors
```

**Query Parameters:**
- `region` (optional): Filter by region (US, Global, Europe, etc.)
- `asset_class` (optional): Filter by asset class
- `frequency` (optional): Filter by frequency (Daily, Monthly)
- `group_id` (optional): Filter by factor group ID
- `search` (optional): Search by name or code
- `limit` (optional, default: 100): Maximum results
- `offset` (optional, default: 0): Pagination offset

**Response:**
```json
[
  {
    "id": 1,
    "code": "qmj_us",
    "name": "Quality Minus Junk - US",
    "region": "US",
    "frequency": "Monthly",
    "annualized_return": 0.082,
    "annualized_volatility": 0.145,
    "sharpe_ratio": 0.565
  }
]
```

#### Get Factor Details
```http
GET /api/factors/{factor_id}
```

Returns detailed information including all cached statistics.

#### Get Factor Time Series
```http
GET /api/factors/{factor_id}/timeseries
```

**Query Parameters:**
- `start_date` (optional): Start date (YYYY-MM-DD)
- `end_date` (optional): End date (YYYY-MM-DD)
- `cumulative` (optional, default: true): Include cumulative returns

#### Get Rolling Statistics
```http
GET /api/factors/{factor_id}/rolling
```

**Query Parameters:**
- `window_length` (default: 36): Rolling window in periods
- `metric` (default: "return"): Metric to compute (return, volatility, sharpe)

#### Get Factor Statistics
```http
GET /api/factors/{factor_id}/statistics
```

**Query Parameters:**
- `start_date` (optional): Start date
- `end_date` (optional): End date

---

### Analytics

#### Compare Factors
```http
GET /api/analytics/comparison
```

**Query Parameters:**
- `factor_ids` (required, multiple): List of factor IDs to compare
- `start_date` (optional): Start date
- `end_date` (optional): End date

**Example:**
```
GET /api/analytics/comparison?factor_ids=1&factor_ids=2&factor_ids=3
```

#### Correlation Matrix
```http
GET /api/analytics/correlation
```

**Query Parameters:**
- `factor_ids` (required, multiple): List of factor IDs
- `start_date` (optional): Start date
- `end_date` (optional): End date

#### Top Factors
```http
GET /api/analytics/top-factors
```

**Query Parameters:**
- `period` (default: "all_time"): Time period (all_time, last_1y, last_3y, last_5y, last_10y)
- `metric` (default: "annualized_return"): Ranking metric (annualized_return, sharpe_ratio)
- `limit` (default: 10): Number of results
- `region` (optional): Filter by region

---

### Advanced Analytics

#### Factor Regression
```http
POST /api/advanced/regression
```

Perform multi-factor regression analysis.

**Query Parameters:**
- `dependent_factor_id` (required): Dependent variable factor ID
- `independent_factor_ids` (required, multiple): Independent variable factor IDs
- `start_date` (optional): Start date
- `end_date` (optional): End date

**Response:**
```json
{
  "dependent_factor_code": "qmj_us",
  "independent_factor_codes": ["bab_us", "mom_us"],
  "coefficients": [0.45, 0.32],
  "intercept": 0.002,
  "r_squared": 0.67,
  "adjusted_r_squared": 0.65,
  "residual_volatility": 0.08,
  "observations": 120
}
```

#### Portfolio Optimization
```http
POST /api/advanced/portfolio-optimization
```

Optimize portfolio weights for a set of factors.

**Query Parameters:**
- `factor_ids` (required, multiple): Factor IDs to include
- `method` (default: "sharpe"): Optimization method (sharpe, min_vol, max_return)
- `target_return` (optional): Target return for min_vol method
- `start_date` (optional): Start date for historical data
- `end_date` (optional): End date for historical data

**Response:**
```json
{
  "weights": [
    {"factor_id": 1, "factor_code": "qmj_us", "weight": 0.35},
    {"factor_id": 2, "factor_code": "bab_us", "weight": 0.45},
    {"factor_id": 3, "factor_code": "mom_us", "weight": 0.20}
  ],
  "expected_return": 0.092,
  "expected_volatility": 0.125,
  "sharpe_ratio": 0.736,
  "optimization_method": "sharpe"
}
```

#### Performance Attribution
```http
POST /api/advanced/performance-attribution
```

Attribute portfolio performance to individual factors.

**Query Parameters:**
- `portfolio_weights`: List of {factor_id: int, weight: float}
- `start_date` (required): Start date
- `end_date` (required): End date

---

### Data Export

#### Export Factor to CSV
```http
GET /api/export/factor/{factor_id}/csv
```

Downloads factor time series as CSV file.

**Query Parameters:**
- `start_date` (optional): Start date
- `end_date` (optional): End date

#### Export Factor to Excel
```http
GET /api/export/factor/{factor_id}/excel
```

Downloads comprehensive Excel workbook with:
- Returns data with cumulative calculations
- Factor metadata
- Summary statistics

#### Export All Factors Summary
```http
GET /api/export/factors/summary/csv
```

Downloads CSV with summary statistics for all factors.

**Query Parameters:**
- `region` (optional): Filter by region

---

### Monitoring & Health

#### Detailed Health Check
```http
GET /api/monitoring/health/detailed
```

Returns comprehensive health status including:
- Database connectivity
- Redis cache status
- System timestamp

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "checks": {
    "database": {"status": "healthy"},
    "redis": {"status": "healthy"}
  }
}
```

#### System Statistics
```http
GET /api/monitoring/stats
```

Returns system-wide statistics:
- Total factors and returns
- Date ranges
- Factor counts by region

#### API Version
```http
GET /api/monitoring/version
```

Returns API version and feature list.

---

## Metadata Endpoints

### Get Regions
```http
GET /api/regions
```

Returns list of available regions.

### Get Asset Classes
```http
GET /api/asset-classes
```

Returns list of available asset classes.

### Get Frequencies
```http
GET /api/frequencies
```

Returns list of available data frequencies.

---

## Error Responses

All endpoints return standard HTTP status codes:

- `200 OK`: Success
- `400 Bad Request`: Invalid parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

**Error Response Format:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Rate Limiting

Currently no rate limiting is enforced. For production:
- Implement rate limiting middleware
- Typical limits: 100 requests/minute per IP
- Use Redis for distributed rate limiting

---

## Caching

The API uses Redis caching for expensive operations:
- Default TTL: 1 hour
- Cache keys include request parameters
- Cache automatically invalidates on data updates

To clear cache:
- Restart the backend service
- Or implement cache invalidation endpoints

---

## WebSocket Support

Future feature: Real-time factor updates via WebSocket.

---

## Best Practices

1. **Use pagination** for large result sets
2. **Specify date ranges** to limit data transfer
3. **Cache responses** on the client side
4. **Use bulk endpoints** when comparing multiple factors
5. **Export data** for offline analysis rather than repeated API calls

---

## Examples

### Python Client Example
```python
import requests

BASE_URL = "http://localhost:8000"

# Get all factors
response = requests.get(f"{BASE_URL}/api/factors")
factors = response.json()

# Get time series
factor_id = factors[0]["id"]
response = requests.get(
    f"{BASE_URL}/api/factors/{factor_id}/timeseries",
    params={"start_date": "2020-01-01", "end_date": "2023-12-31"}
)
timeseries = response.json()

# Compare factors
response = requests.get(
    f"{BASE_URL}/api/analytics/comparison",
    params={"factor_ids": [1, 2, 3]}
)
comparison = response.json()
```

### JavaScript/TypeScript Example
```typescript
const BASE_URL = "http://localhost:8000";

// Get factors with filtering
const response = await fetch(
  `${BASE_URL}/api/factors?region=US&frequency=Monthly`
);
const factors = await response.json();

// Export to Excel
const factor_id = factors[0].id;
const exportResponse = await fetch(
  `${BASE_URL}/api/export/factor/${factor_id}/excel`
);
const blob = await exportResponse.blob();
// Download file...
```

---

## Support

For API issues or questions:
- Check the interactive docs at `/api/docs`
- Review error messages for debugging
- Check system health at `/api/monitoring/health/detailed`

---

**Version**: 1.0.0
**Last Updated**: 2024
