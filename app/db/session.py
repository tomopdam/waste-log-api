import logging

from sqlmodel import Session, SQLModel, create_engine

from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG, pool_pre_ping=True)


def create_db_and_tables():
    """Create database tables if they don't exist"""
    logger.info("Creating database tables")
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get a database session"""
    with Session(engine) as session:
        yield session
