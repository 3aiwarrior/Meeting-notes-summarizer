"""
Database configuration and session management.

Provides SQLAlchemy engine, session factory, and base model class.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from app.core.settings import settings

# Create SQLAlchemy engine
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Reason: Verify connections before using them
    pool_size=5,  # Reason: Limit concurrent DB connections
    max_overflow=10,  # Reason: Allow temporary connection bursts
    echo=settings.debug,  # Reason: Log SQL queries in debug mode
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency injection for database sessions.

    Yields:
        Session: SQLAlchemy database session

    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database tables.

    Creates all tables defined in models if they don't exist.
    """
    # Import all models to register them with Base
    from app.models import audio, summary, transcription  # noqa: F401

    Base.metadata.create_all(bind=engine)
