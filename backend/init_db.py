#!/usr/bin/env python3
"""
Database initialization script
Run this to set up the PostgreSQL database for the first time
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from database import DATABASE_URL, SessionLocal, drop_db, init_db
from models import User
from auth import hash_password


def create_database():
    """Create the database if it doesn't exist"""
    # Extract database name from URL
    db_name = DATABASE_URL.split("/")[-1].split("?")[0]
    base_url = "/".join(DATABASE_URL.split("/")[:-1])

    print(f"Creating database: {db_name}")
    print(f"Connection: {base_url}")

    try:
        # Connect to postgres database to create our database
        engine = create_engine(f"{base_url}/postgres", isolation_level="AUTOCOMMIT")

        with engine.connect() as conn:
            # Check if database exists
            result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"))

            if result.fetchone():
                print(f"✅ Database '{db_name}' already exists")
            else:
                # Create database
                conn.execute(text(f"CREATE DATABASE {db_name}"))
                print(f"✅ Database '{db_name}' created successfully")

        engine.dispose()

    except Exception as e:
        print(f"❌ Error creating database: {e}")
        print("\nPlease ensure:")
        print("1. PostgreSQL is running")
        print("2. Connection details in .env are correct")
        print("3. User has permission to create databases")
        sys.exit(1)


def create_default_admin():
    """Create default admin user if it doesn't exist"""
    print()
    print("Setting up default admin user...")

    db = SessionLocal()
    try:
        # Check if admin user already exists
        existing_admin = db.query(User).filter(User.username == "admin").first()

        if existing_admin:
            print("✅ Admin user already exists")
        else:
            # Create default admin user
            admin_user = User(
                username="admin",
                email="admin@investory.dev",
                hashed_password=hash_password("admin123"),
                full_name="Administrator",
                role="admin",
                requires_password_change=True,  # Force password change on first login
                is_active=True
            )

            db.add(admin_user)
            db.commit()

            print("✅ Default admin user created")
            print()
            print("=" * 60)
            print("⚠️  IMPORTANT: Default Admin Credentials")
            print("=" * 60)
            print("  Username: admin")
            print("  Password: admin123")
            print()
            print("  ⚠️  You MUST change this password on first login!")
            print("=" * 60)

    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """Main initialization function"""
    print("=" * 60)
    print("Investory Database Setup")
    print("=" * 60)
    print()

    # Check if DATABASE_URL is set
    if not DATABASE_URL or DATABASE_URL == "postgresql://postgres:postgres@localhost:5432/investory":
        print("⚠️  Using default DATABASE_URL")
        print("   Consider setting a custom DATABASE_URL in .env file")
        print()

    # Create database
    create_database()

    print()
    print("Creating tables...")

    try:
        # Initialize database tables
        init_db()
        print()
        print("=" * 60)
        print("✅ Database setup complete!")
        print("=" * 60)
        print()
        print("Tables created:")
        print("  - users")
        print("  - analyses")
        print("  - watchlists")
        print("  - stock_cache")
        print("  - api_usage")
        print()

        # Create default admin user
        create_default_admin()

        print()
        print("You can now start the API server with:")
        print("  python main.py")
        print()

    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
