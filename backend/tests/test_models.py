"""
Tests for database models
"""
import pytest
from datetime import date, datetime

from backend.models import Factor, FactorReturn, FactorGroup


def test_create_factor_group(db_session):
    """Test creating a factor group"""
    group = FactorGroup(
        code="test_group",
        name="Test Group",
        description="A test factor group"
    )
    db_session.add(group)
    db_session.commit()

    assert group.id is not None
    assert group.code == "test_group"
    assert group.created_at is not None


def test_create_factor(db_session):
    """Test creating a factor"""
    factor = Factor(
        code="test_factor",
        name="Test Factor",
        provider="AQR",
        region="US",
        asset_class="Equity",
        frequency="Monthly",
        first_date=date(2020, 1, 1),
        last_date=date(2020, 12, 31)
    )
    db_session.add(factor)
    db_session.commit()

    assert factor.id is not None
    assert factor.code == "test_factor"
    assert factor.created_at is not None


def test_factor_with_group(db_session):
    """Test factor relationship with group"""
    group = FactorGroup(code="value", name="Value")
    db_session.add(group)
    db_session.commit()

    factor = Factor(
        code="hml",
        name="HML",
        group_id=group.id,
        region="US"
    )
    db_session.add(factor)
    db_session.commit()
    db_session.refresh(factor)

    assert factor.group.code == "value"


def test_factor_returns(db_session):
    """Test factor returns relationship"""
    factor = Factor(code="test", name="Test", region="US")
    db_session.add(factor)
    db_session.commit()
    db_session.refresh(factor)

    returns = [
        FactorReturn(factor_id=factor.id, date=date(2020, 1, 1), return_value=0.01),
        FactorReturn(factor_id=factor.id, date=date(2020, 2, 1), return_value=0.02),
        FactorReturn(factor_id=factor.id, date=date(2020, 3, 1), return_value=-0.01),
    ]
    for ret in returns:
        db_session.add(ret)
    db_session.commit()

    db_session.refresh(factor)
    assert len(factor.returns) == 3


def test_factor_return_unique_constraint(db_session):
    """Test that duplicate date returns are not allowed"""
    factor = Factor(code="test", name="Test", region="US")
    db_session.add(factor)
    db_session.commit()
    db_session.refresh(factor)

    ret1 = FactorReturn(factor_id=factor.id, date=date(2020, 1, 1), return_value=0.01)
    db_session.add(ret1)
    db_session.commit()

    # Try to add duplicate
    ret2 = FactorReturn(factor_id=factor.id, date=date(2020, 1, 1), return_value=0.02)
    db_session.add(ret2)

    with pytest.raises(Exception):  # Should raise integrity error
        db_session.commit()
