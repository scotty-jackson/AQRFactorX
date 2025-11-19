"""
Tests for factor API endpoints
"""
import pytest
from datetime import date

from backend.models import Factor, FactorReturn, FactorGroup


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_list_factors_empty(client):
    """Test listing factors when database is empty"""
    response = client.get("/api/factors")
    assert response.status_code == 200
    assert response.json() == []


def test_list_factors(client, db_session, sample_factor_data):
    """Test listing factors"""
    # Create a test factor
    factor = Factor(**sample_factor_data)
    db_session.add(factor)
    db_session.commit()

    response = client.get("/api/factors")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["code"] == "test_qmj_us"
    assert data[0]["name"] == "Test Quality Minus Junk"


def test_get_factor_by_id(client, db_session, sample_factor_data):
    """Test getting a specific factor"""
    factor = Factor(**sample_factor_data)
    db_session.add(factor)
    db_session.commit()
    db_session.refresh(factor)

    response = client.get(f"/api/factors/{factor.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "test_qmj_us"
    assert data["annualized_return"] == 0.08


def test_get_factor_not_found(client):
    """Test getting a non-existent factor"""
    response = client.get("/api/factors/9999")
    assert response.status_code == 404


def test_filter_factors_by_region(client, db_session, sample_factor_data):
    """Test filtering factors by region"""
    # Create factors in different regions
    factor_us = Factor(**sample_factor_data)
    db_session.add(factor_us)

    factor_europe = Factor(**{**sample_factor_data, "code": "test_qmj_eu", "region": "Europe"})
    db_session.add(factor_europe)
    db_session.commit()

    # Filter by US
    response = client.get("/api/factors?region=US")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["region"] == "US"


def test_search_factors(client, db_session, sample_factor_data):
    """Test searching factors"""
    factor = Factor(**sample_factor_data)
    db_session.add(factor)
    db_session.commit()

    response = client.get("/api/factors?search=quality")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert "Quality" in data[0]["name"]


def test_get_factor_timeseries(client, db_session, sample_factor_data):
    """Test getting factor time series"""
    # Create factor with returns
    factor = Factor(**sample_factor_data)
    db_session.add(factor)
    db_session.commit()
    db_session.refresh(factor)

    # Add some returns
    returns = [
        FactorReturn(factor_id=factor.id, date=date(2020, 1, 1), return_value=0.02),
        FactorReturn(factor_id=factor.id, date=date(2020, 2, 1), return_value=-0.01),
        FactorReturn(factor_id=factor.id, date=date(2020, 3, 1), return_value=0.03),
    ]
    for ret in returns:
        db_session.add(ret)
    db_session.commit()

    response = client.get(f"/api/factors/{factor.id}/timeseries")
    assert response.status_code == 200
    data = response.json()
    assert data["factor_code"] == "test_qmj_us"
    assert len(data["data"]) == 3
    assert data["data"][0]["return_value"] == 0.02


def test_get_factor_statistics(client, db_session, sample_factor_data):
    """Test getting factor statistics"""
    factor = Factor(**sample_factor_data)
    db_session.add(factor)
    db_session.commit()
    db_session.refresh(factor)

    # Add returns
    returns = [
        FactorReturn(factor_id=factor.id, date=date(2020, i, 1), return_value=0.01)
        for i in range(1, 13)
    ]
    for ret in returns:
        db_session.add(ret)
    db_session.commit()

    response = client.get(f"/api/factors/{factor.id}/statistics")
    assert response.status_code == 200
    data = response.json()
    assert data["factor_code"] == "test_qmj_us"
    assert "annualized_return" in data
    assert "sharpe_ratio" in data


def test_pagination(client, db_session, sample_factor_data):
    """Test factor list pagination"""
    # Create multiple factors
    for i in range(15):
        factor_data = {**sample_factor_data, "code": f"test_factor_{i}"}
        factor = Factor(**factor_data)
        db_session.add(factor)
    db_session.commit()

    # Test limit
    response = client.get("/api/factors?limit=5")
    assert response.status_code == 200
    assert len(response.json()) == 5

    # Test offset
    response = client.get("/api/factors?limit=5&offset=10")
    assert response.status_code == 200
    assert len(response.json()) == 5
