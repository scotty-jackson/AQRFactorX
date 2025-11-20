"""
Tests for analytics API endpoints
"""
import pytest
from datetime import date

from backend.models import Factor, FactorReturn



def test_compare_factors(client, db_session):
    """Test factor comparison endpoint"""
    # Create two factors with returns
    factor1 = Factor(
        code="test_factor_1",
        name="Test Factor 1",
        region="US",
        frequency="Monthly",
        first_date=date(2020, 1, 1),
        last_date=date(2020, 12, 31)
    )
    factor2 = Factor(
        code="test_factor_2",
        name="Test Factor 2",
        region="US",
        frequency="Monthly",
        first_date=date(2020, 1, 1),
        last_date=date(2020, 12, 31)
    )
    db_session.add(factor1)
    db_session.add(factor2)
    db_session.commit()
    db_session.refresh(factor1)
    db_session.refresh(factor2)

    # Add returns
    for i in range(1, 6):
        db_session.add(FactorReturn(
            factor_id=factor1.id,
            date=date(2020, i, 1),
            return_value=0.01
        ))
        db_session.add(FactorReturn(
            factor_id=factor2.id,
            date=date(2020, i, 1),
            return_value=0.02
        ))
    db_session.commit()

    response = client.get(
        f"/api/analytics/comparison?factor_ids={factor1.id}&factor_ids={factor2.id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["factors"]) == 2


def test_compare_factors_minimum_requirement(client):
    """Test comparison requires at least 2 factors"""
    response = client.get("/api/analytics/comparison?factor_ids=1")
    assert response.status_code == 400


def test_correlation_matrix(client, db_session):
    """Test correlation matrix computation"""
    # Create factors with correlated returns
    factor1 = Factor(code="f1", name="Factor 1", region="US", frequency="Monthly")
    factor2 = Factor(code="f2", name="Factor 2", region="US", frequency="Monthly")
    db_session.add(factor1)
    db_session.add(factor2)
    db_session.commit()
    db_session.refresh(factor1)
    db_session.refresh(factor2)

    # Add returns
    for i in range(1, 13):
        db_session.add(FactorReturn(
            factor_id=factor1.id,
            date=date(2020, i, 1),
            return_value=0.01 * i
        ))
        db_session.add(FactorReturn(
            factor_id=factor2.id,
            date=date(2020, i, 1),
            return_value=0.01 * i * 1.5
        ))
    db_session.commit()

    response = client.get(
        f"/api/analytics/correlation?factor_ids={factor1.id}&factor_ids={factor2.id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert "correlations" in data
    assert len(data["factor_codes"]) == 2


def test_top_factors(client, db_session):
    """Test top factors endpoint"""
    # Create factors with different returns
    for i in range(5):
        factor = Factor(
            code=f"factor_{i}",
            name=f"Factor {i}",
            region="US",
            frequency="Monthly",
            annualized_return=0.05 * (i + 1)
        )
        db_session.add(factor)
        db_session.commit()
        db_session.refresh(factor)

        # Add returns
        for month in range(1, 13):
            db_session.add(FactorReturn(
                factor_id=factor.id,
                date=date(2020, month, 1),
                return_value=0.01 * (i + 1)
            ))
    db_session.commit()

    response = client.get("/api/analytics/top-factors?limit=3")
    assert response.status_code == 200
    data = response.json()
    assert len(data["factors"]) <= 3
