# Docker Setup Guide

This guide explains how to run the Investory using Docker.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 2GB+ available disk space
- Alpha Vantage API key

## Quick Start

### 1. Clone and Configure

```bash
# Navigate to project directory
cd investory

# Copy environment file
cp .env.example .env

# Edit .env and add your Alpha Vantage API key
nano .env
```

### 2. Start the Application

```bash
# Build and start all services
docker compose up -d

# View logs
docker compose logs -f

# Check service status
docker compose ps
```

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **pgAdmin** (optional): http://localhost:5050

### 4. Stop the Application

```bash
# Stop all services
docker compose down

# Stop and remove volumes (⚠️ deletes data)
docker compose down -v
```

## Services

### PostgreSQL Database
- **Image**: postgres:14-alpine
- **Port**: 5432
- **Data**: Persisted in Docker volume `postgres_data`
- **Health Check**: Automatic with retry logic

### Backend API
- **Built from**: `backend/Dockerfile`
- **Port**: 8000
- **Environment**: Auto-configured via docker compose
- **Auto-restart**: Enabled
- **Database Init**: Runs automatically on startup

### Frontend
- **Built from**: `frontend/Dockerfile`
- **Port**: 3000 (mapped to 80 in container)
- **Nginx**: Serves static files
- **API Proxy**: Automatically configured

### pgAdmin (Optional)
- **Image**: dpage/pgadmin4
- **Port**: 5050
- **Usage**: Database management UI
- **Enable**: `docker compose --profile tools up -d`

## Docker Compose Commands

### Basic Operations

```bash
# Start services
docker compose up -d

# Start with rebuild
docker compose up -d --build

# View logs
docker compose logs -f [service_name]

# Restart a service
docker compose restart [service_name]

# Stop services
docker compose stop

# Remove services
docker compose down

# Remove services and volumes
docker compose down -v
```

### Development

```bash
# Build images
docker compose build

# Rebuild a specific service
docker compose build backend

# Execute command in running container
docker compose exec backend python init_db.py

# Open shell in container
docker compose exec backend sh
docker compose exec db psql -U postgres -d investory
```

### Monitoring

```bash
# View service status
docker compose ps

# View resource usage
docker stats

# View logs for specific service
docker compose logs backend
docker compose logs -f frontend

# Follow logs from all services
docker compose logs -f
```

## Environment Variables

Edit `.env` file to configure:

```env
# Database
DB_NAME=investory
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_PORT=5432

# API
ALPHA_VANTAGE_KEY=your_api_key_here
BACKEND_PORT=8000

# Frontend
FRONTEND_PORT=3000

# pgAdmin (optional)
PGADMIN_EMAIL=admin@rule1.com
PGADMIN_PASSWORD=admin
PGADMIN_PORT=5050
```

## Production Deployment

### Using Production Compose File

```bash
# Copy production environment
cp .env.example .env.prod

# Edit production settings
nano .env.prod

# Start production stack
docker compose -f docker compose.prod.yml --env-file .env.prod up -d

# View logs
docker compose -f docker compose.prod.yml logs -f
```

### Production Features

- **Multiple Workers**: Backend runs with 4 Uvicorn workers
- **Nginx Reverse Proxy**: Handles SSL, caching, load balancing
- **Auto-restart**: All services restart on failure
- **Health Checks**: Automatic service health monitoring
- **Optimized Builds**: Multi-stage builds for smaller images

### SSL Configuration

1. Obtain SSL certificates (Let's Encrypt recommended)
2. Place certificates in `nginx/ssl/`
3. Update `nginx/conf.d/default.conf`
4. Restart nginx: `docker compose restart nginx`

## Database Management

### Access Database

```bash
# Using psql from host
docker compose exec db psql -U postgres -d investory

# Using psql commands
docker compose exec db psql -U postgres -d investory -c "SELECT COUNT(*) FROM analyses;"
```

### Backup Database

```bash
# Create backup
docker compose exec db pg_dump -U postgres investory > backup_$(date +%Y%m%d).sql

# Restore backup
cat backup_20240213.sql | docker compose exec -T db psql -U postgres -d investory
```

### Reset Database

```bash
# ⚠️ This deletes all data!
docker compose down -v
docker compose up -d
```

## Troubleshooting

### Port Conflicts

If ports are already in use:

```bash
# Change ports in .env
BACKEND_PORT=8001
FRONTEND_PORT=3001
DB_PORT=5433

# Restart services
docker compose down
docker compose up -d
```

### Container Won't Start

```bash
# View detailed logs
docker compose logs [service_name]

# Rebuild from scratch
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

### Database Connection Issues

```bash
# Check database is running
docker compose ps db

# Check database logs
docker compose logs db

# Verify connection string in .env
DATABASE_URL=postgresql://postgres:postgres@db:5432/investory
```

### "Database not found" Error

```bash
# Initialize database manually
docker compose exec backend python init_db.py

# Or restart backend to auto-initialize
docker compose restart backend
```

### Frontend Can't Reach Backend

```bash
# Check backend is running
curl http://localhost:8000/

# Check nginx proxy configuration
docker compose exec frontend cat /etc/nginx/conf.d/default.conf

# View frontend logs
docker compose logs frontend
```

## Performance Optimization

### Image Size Reduction

```bash
# View image sizes
docker images | grep rule1

# Use multi-stage builds (already configured)
# Remove development dependencies
# Use alpine base images
```

### Build Cache

```bash
# Clear build cache
docker builder prune -a

# Build without cache
docker compose build --no-cache
```

### Volume Management

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect investory_postgres_data

# Remove unused volumes
docker volume prune
```

## Development Workflow

### Hot Reload

Development mode includes hot reload:

```bash
# Backend: Auto-reloads on code changes
docker compose up -d

# Frontend: Requires rebuild
# Edit frontend code
docker compose build frontend
docker compose up -d frontend
```

### Installing New Dependencies

**Backend:**
```bash
# Add to requirements.txt
echo "requests==2.31.0" >> backend/requirements.txt

# Rebuild
docker compose build backend
docker compose up -d backend
```

**Frontend:**
```bash
# Build container with shell access
docker compose run --rm frontend sh

# Inside container
npm install package-name

# Exit and rebuild
docker compose build frontend
```

## Best Practices

### Security

- Change default passwords in `.env`
- Use secrets management in production
- Enable firewall rules
- Regular security updates
- Use non-root users (already configured)

### Monitoring

```bash
# Set up monitoring stack
docker compose -f docker compose.monitoring.yml up -d

# View metrics
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3001
```

### Backups

```bash
# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker compose exec -T db pg_dump -U postgres investory > "backups/backup_$DATE.sql"
find backups/ -mtime +30 -delete
```

Add to crontab:
```bash
0 2 * * * /path/to/backup-script.sh
```

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)
- [Nginx Docker Hub](https://hub.docker.com/_/nginx)

## Support

For issues:
1. Check logs: `docker compose logs -f`
2. Verify configuration: `.env` file
3. Check service health: `docker compose ps`
4. Restart services: `docker compose restart`
5. Rebuild if needed: `docker compose up -d --build`
