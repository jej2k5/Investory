"""
Database configuration and session management
"""

import os
from contextlib import contextmanager

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

load_dotenv()

# Database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/investory")

# For SQLite (development/testing)
# DATABASE_URL = "sqlite:///./investory.db"

# Create engine
if DATABASE_URL.startswith("sqlite"):
    # SQLite specific configuration
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # PostgreSQL configuration
    engine = create_engine(
        DATABASE_URL,
        pool_size=20,
        max_overflow=0,
        pool_pre_ping=True,
        pool_recycle=3600,
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """
    Dependency function to get database session.
    Use with FastAPI's Depends() for automatic cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager for database sessions.
    Use in scripts or non-FastAPI contexts.

    Example:
        with get_db_context() as db:
            user = db.query(User).first()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """
    Initialize database - create all tables.
    Run this once to set up the database schema.
    """
    from models import Base

    Base.metadata.create_all(bind=engine)
    ensure_watchlist_schema_compatibility()
    print("✅ Database tables created successfully!")


def ensure_watchlist_schema_compatibility() -> None:
    """
    Backfill missing columns in `watchlists` for environments that created the
    table before moat/growth snapshot fields were added.

    SQLAlchemy's `create_all()` does not alter existing tables, so this keeps
    long-lived databases compatible without requiring Alembic migrations.
    """

    watchlist_columns = {
        "moat_score": "INTEGER",
        "moat_assessment": "VARCHAR(50)",
        "has_wide_moat": "BOOLEAN",
        "book_value_growth": "FLOAT",
        "eps_growth": "FLOAT",
        "cash_flow_growth": "FLOAT",
        "sales_growth": "FLOAT",
        "roic": "FLOAT",
        "notes": "TEXT",
    }

    inspector = inspect(engine)
    if "watchlists" not in inspector.get_table_names():
        return

    existing = {column["name"] for column in inspector.get_columns("watchlists")}
    missing = [name for name in watchlist_columns if name not in existing]
    if not missing:
        return

    with engine.begin() as connection:
        for column_name in missing:
            column_type = watchlist_columns[column_name]
            connection.execute(text(f"ALTER TABLE watchlists ADD COLUMN {column_name} {column_type}"))
    print(f"✅ Added missing watchlists columns: {', '.join(missing)}")


def drop_db():
    """
    Drop all tables - WARNING: This deletes all data!
    Only use in development.
    """
    from models import Base

    Base.metadata.drop_all(bind=engine)
    print("⚠️  All database tables dropped!")


if __name__ == "__main__":
    # Run this file directly to initialize the database
    print(f"Database URL: {DATABASE_URL}")
    init_db()
