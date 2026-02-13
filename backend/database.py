"""
Database configuration and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/rule1_investing"
)

# For SQLite (development/testing)
# DATABASE_URL = "sqlite:///./rule1_investing.db"

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
    print("✅ Database tables created successfully!")

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
