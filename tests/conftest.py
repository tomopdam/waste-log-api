import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Setup the database for testing."""
    from sqlmodel import SQLModel

    from app.db.session import create_db_and_tables, engine

    # Create the database tables
    create_db_and_tables()

    # Drop all tables after tests are done
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture()
def session():
    """Create a new database session for each test."""
    from app.db.session import get_session

    gen = get_session()
    session = next(gen)
    try:
        yield session
    finally:
        # cleanup: close DB session (important!)
        session.close()
        try:
            next(gen)  # allow generator to finish if needed
        except StopIteration:
            pass


@pytest.fixture(scope="function")
def client():
    with TestClient(app) as c:
        yield c
