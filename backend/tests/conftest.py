"""
Pytest configuration and fixtures
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.main import app
from backend.models import Base
from backend.db import get_db

# Use in-memory SQLite for tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False)

@pytest.fixture(scope="session")
def db_engine():
    """Create engine once for the session"""
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    """
    Connect to the database, start a transaction,
    and yield a session bound to that transaction.
    Rollback after the test.
    """
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with the session override"""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


from datetime import date

@pytest.fixture
def sample_factor_data():
    """Sample factor data for testing"""
    return {
        "code": "test_qmj_us",
        "name": "Test Quality Minus Junk",
        "provider": "AQR",
        "region": "US",
        "asset_class": "Equity",
        "frequency": "Monthly",
        "description": "Test factor for unit tests",
        "first_date": date(2020, 1, 1),
        "last_date": date(2020, 12, 31),
        "annualized_return": 0.08,
        "annualized_volatility": 0.15,
        "sharpe_ratio": 0.53,
        "max_drawdown": -0.12
    }
