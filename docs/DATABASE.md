# PostgreSQL Database Setup Guide

This guide will help you set up PostgreSQL for the Investory.

## Quick Start

### Option 1: Docker (Recommended for Development)

```bash
# Start PostgreSQL with Docker
docker run -d \
  --name investory-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=investory \
  -p 5432:5432 \
  -v rule1_data:/var/lib/postgresql/data \
  postgres:14-alpine

# Wait a few seconds for PostgreSQL to start, then initialize the database
cd backend
python init_db.py
```

### Option 2: Local PostgreSQL Installation

#### macOS (using Homebrew)
```bash
# Install PostgreSQL
brew install postgresql@14

# Start PostgreSQL
brew services start postgresql@14

# Create database
createdb investory

# Initialize tables
cd backend
python init_db.py
```

#### Ubuntu/Debian
```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql -c "CREATE DATABASE investory;"
sudo -u postgres psql -c "CREATE USER rule1user WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE investory TO rule1user;"

# Update .env with your credentials
# DATABASE_URL=postgresql://rule1user:your_password@localhost:5432/investory

# Initialize tables
cd backend
python init_db.py
```

#### Windows
```powershell
# Download and install PostgreSQL from:
# https://www.postgresql.org/download/windows/

# After installation, open pgAdmin4 and create a database named 'investory'

# Update .env with your credentials
# Then initialize tables:
cd backend
python init_db.py
```

## Environment Configuration

Create or update `.env` file in the `backend` directory:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/investory

# For production, use a more secure password:
# DATABASE_URL=postgresql://username:securepassword@hostname:5432/investory

# Alpha Vantage API Key
ALPHA_VANTAGE_KEY=your_api_key_here
```

## Database Schema

The application uses the following tables:

### `users`
Stores user account information
- `id`: Primary key
- `email`: Unique email address
- `hashed_password`: Hashed password
- `full_name`: Optional user name
- `created_at`: Account creation timestamp
- `last_login`: Last login timestamp
- `is_active`: Account status

### `analyses`
Stores stock analyses with Four Ms scores
- `id`: Primary key
- `user_id`: Foreign key to users (optional)
- `symbol`: Stock ticker symbol
- `company_name`: Company name
- `meaning_score`: Score 1-5
- `moat_score`: Score 1-5
- `management_score`: Score 1-5
- `margin_score`: Score 1-5
- `overall_score`: Calculated average
- `recommendation`: Buy/Hold/Pass
- `current_price`: Price at analysis
- `sticker_price`: Calculated intrinsic value
- `mos_price`: Margin of safety price
- `book_value_growth`: Growth rate %
- `eps_growth`: Growth rate %
- `cash_flow_growth`: Growth rate %
- `sales_growth`: Growth rate %
- `roic`: Return on invested capital %
- `user_notes`: Free-form notes
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### `watchlists`
Stores user watchlist items
- `id`: Primary key
- `user_id`: Foreign key to users
- `symbol`: Stock ticker symbol
- `company_name`: Company name
- `target_buy_price`: Target buy price
- `target_sell_price`: Target sell price
- `alert_enabled`: Price alert enabled
- `alert_price`: Alert trigger price
- `notes`: User notes
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### `stock_cache`
Caches stock data to reduce API calls
- `id`: Primary key
- `symbol`: Stock ticker symbol (unique)
- `company_name`: Company name
- All financial metrics and growth rates
- `fetched_at`: When data was fetched
- `expires_at`: When cache expires (1 hour TTL)

### `api_usage`
Tracks API usage for analytics and rate limiting
- `id`: Primary key
- `user_id`: Foreign key to users (optional)
- `endpoint`: API endpoint called
- `method`: HTTP method
- `status_code`: Response status
- `response_time_ms`: Response time
- `ip_address`: Client IP
- `user_agent`: Client user agent
- `created_at`: Request timestamp

## Database Operations

### Initialize Database
```bash
python init_db.py
```

### Reset Database (⚠️ Deletes all data)
```python
from database import drop_db, init_db

drop_db()  # Drop all tables
init_db()  # Create tables fresh
```

### View Database Contents
```bash
# Using psql command line
psql -d investory

# List all tables
\dt

# View analyses
SELECT id, symbol, overall_score, recommendation, created_at FROM analyses;

# View cached stocks
SELECT symbol, company_name, fetched_at, expires_at FROM stock_cache;

# Exit psql
\q
```

### Backup Database
```bash
# Create backup
pg_dump investory > backup_$(date +%Y%m%d).sql

# Restore from backup
psql investory < backup_20240213.sql
```

## Migrations (Future)

For schema changes in production, use Alembic:

```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Connection Testing

Test your database connection:

```python
from database import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        print("✅ Database connection successful!")
        print(f"PostgreSQL version: {result.fetchone()[0]}")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
```

## Performance Optimization

### Indexes
The following indexes are automatically created:
- `users.email` - Unique index for fast login lookups
- `analyses.symbol` - For filtering by stock symbol
- `analyses.created_at` - For sorting by date
- `analyses.user_id` - For user's analyses
- `watchlists.user_id` - For user's watchlist
- `watchlists.symbol` - For stock lookups
- `stock_cache.symbol` - Unique index for cache lookups
- `api_usage.endpoint` - For analytics
- `api_usage.created_at` - For time-based queries

### Connection Pooling
The application uses SQLAlchemy's connection pooling:
- Pool size: 20 connections
- Max overflow: 0
- Pool pre-ping: Enabled (checks connection health)
- Pool recycle: 3600 seconds

## Troubleshooting

### Connection refused
```
psycopg2.OperationalError: could not connect to server
```
**Solution:** Ensure PostgreSQL is running
```bash
# macOS
brew services start postgresql@14

# Linux
sudo systemctl start postgresql

# Docker
docker start investory-postgres
```

### Permission denied
```
psycopg2.OperationalError: FATAL: permission denied for database
```
**Solution:** Grant proper permissions
```sql
GRANT ALL PRIVILEGES ON DATABASE investory TO your_user;
```

### Database doesn't exist
```
psycopg2.OperationalError: database "investory" does not exist
```
**Solution:** Create the database
```bash
createdb investory
```

### Port already in use
```
Error: Port 5432 is already in use
```
**Solution:** Either:
1. Stop other PostgreSQL instance
2. Use different port in DATABASE_URL
3. Check what's using the port: `lsof -i :5432`

## Production Considerations

### Security
- Use strong passwords
- Enable SSL connections
- Restrict network access
- Regular security updates
- Use environment variables (never commit passwords)

### Backups
- Automated daily backups
- Store backups in different location
- Test restore process regularly
- Keep multiple backup versions

### Monitoring
- Set up connection pooling monitoring
- Track query performance
- Monitor disk space usage
- Set up alerts for failures

### High Availability
- Consider read replicas for scaling
- Set up automatic failover
- Use managed database services (AWS RDS, Google Cloud SQL)
- Implement database connection retry logic

## Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [FastAPI Database Tutorial](https://fastapi.tiangolo.com/tutorial/sql-databases/)
