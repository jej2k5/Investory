# 🐳 Docker Quick Start

Run the entire Rule #1 Investing Platform with one command!

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) 20.10+
- [Docker Compose](https://docs.docker.com/compose/install/) 2.0+
- 2GB+ available RAM

## Quick Start (60 seconds)

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Add your Alpha Vantage API key to .env
nano .env  # or use any text editor

# 3. Start everything!
docker compose up -d

# 4. Wait 30 seconds for services to initialize

# 5. Open your browser
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/api/docs
```

That's it! 🎉

## Using Make Commands (Easier)

If you have `make` installed:

```bash
# One command setup
make dev

# View all commands
make help

# Common operations
make up           # Start services
make down         # Stop services
make logs         # View logs
make restart      # Restart all
make db-backup    # Backup database
```

## What Gets Started?

✅ **PostgreSQL Database** (port 5432)
- Persistent data storage
- Auto-initialized schema
- Ready for connections

✅ **Python FastAPI Backend** (port 8000)
- RESTful API
- Auto-connects to database
- OpenAPI documentation

✅ **React Frontend** (port 3000)
- Modern web interface
- Nginx web server
- API proxy configured

✅ **Optional: pgAdmin** (port 5050)
- Database management UI
- `docker compose --profile tools up -d`

## Common Commands

```bash
# View logs
docker compose logs -f

# Stop everything
docker compose down

# Restart a service
docker compose restart backend

# Check status
docker compose ps

# Access database shell
docker compose exec db psql -U postgres -d rule1_investing

# Backup database
docker compose exec db pg_dump -U postgres rule1_investing > backup.sql
```

## Configuration

Edit `.env` file:

```env
# Required
ALPHA_VANTAGE_KEY=your_key_here

# Optional (defaults shown)
BACKEND_PORT=8000
FRONTEND_PORT=3000
DB_PASSWORD=postgres
```

## Troubleshooting

### Port already in use?
Change ports in `.env`:
```env
BACKEND_PORT=8001
FRONTEND_PORT=3001
```

### Services won't start?
```bash
# View detailed logs
docker compose logs backend

# Rebuild everything
docker compose down
docker compose up -d --build
```

### Database connection error?
```bash
# Reset database
docker compose down -v
docker compose up -d
```

## Production Deployment

```bash
# Use production compose file
docker compose -f docker compose.prod.yml up -d

# Or with make
make prod-up
```

## Complete Documentation

- [Docker Setup Guide](docs/DOCKER.md) - Detailed documentation
- [Database Guide](docs/DATABASE.md) - PostgreSQL setup
- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment
- [API Documentation](docs/API.md) - API reference

## Support

Issues? Check:
1. `docker compose logs -f` for errors
2. `.env` file is configured
3. Ports 3000, 8000, 5432 are available
4. Docker and Docker Compose are up to date

## What's Running?

```bash
# Check all services
docker compose ps

# View resource usage
docker stats
```

## Stop Everything

```bash
# Stop services (keeps data)
docker compose down

# Stop and delete data
docker compose down -v
```

---

**Next Steps:**
1. Open http://localhost:3000
2. Search for a stock (e.g., "AAPL")
3. Analyze using the Four Ms
4. Save your analysis

Happy investing! 📈
