#!/usr/bin/env python3
"""
Database initialization script
Run this to set up the PostgreSQL database for the first time
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_db, drop_db, DATABASE_URL
from sqlalchemy import create_engine, text

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
            result = conn.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
            )
            
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

def main():
    """Main initialization function"""
    print("=" * 60)
    print("Rule #1 Investing Database Setup")
    print("=" * 60)
    print()
    
    # Check if DATABASE_URL is set
    if not DATABASE_URL or DATABASE_URL == "postgresql://postgres:postgres@localhost:5432/rule1_investing":
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
        print("You can now start the API server with:")
        print("  python main.py")
        print()
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
