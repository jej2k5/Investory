# Deployment Guide

This guide covers deploying the Rule #1 Investing Platform to production.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Backend Deployment](#backend-deployment)
- [Frontend Deployment](#frontend-deployment)
- [Database Setup](#database-setup)
- [Environment Configuration](#environment-configuration)
- [Monitoring & Logging](#monitoring--logging)

## Prerequisites

- Docker & Docker Compose (recommended)
- OR: Python 3.9+, Node.js 18+, PostgreSQL 14+
- Domain name with SSL certificate
- Alpha Vantage API key

## Deployment Options

### Option 1: Docker Compose (Recommended)

1. Create `docker compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - ALPHA_VANTAGE_KEY=${ALPHA_VANTAGE_KEY}
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@db:5432/rule1_investing
    depends_on:
      - db
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=https://api.yourdomain.com
    depends_on:
      - backend
    restart: unless-stopped

  db:
    image: postgres:14-alpine
    environment:
      - POSTGRES_DB=rule1_investing
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

volumes:
  postgres_data:
```

2. Create backend `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

3. Create frontend `Dockerfile`:

```dockerfile
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

4. Deploy:

```bash
docker compose up -d
```

### Option 2: Traditional Deployment

#### Backend (Python/FastAPI)

**Render.com / Railway:**

1. Connect your GitHub repository
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables

**AWS EC2:**

```bash
# SSH into your EC2 instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Install Python and dependencies
sudo apt update
sudo apt install python3-pip python3-venv nginx

# Clone your repo
git clone https://github.com/yourusername/rule1-app.git
cd rule1-app/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install and configure supervisor
sudo apt install supervisor

# Create supervisor config
sudo nano /etc/supervisor/conf.d/rule1-api.conf
```

Supervisor config:
```ini
[program:rule1-api]
directory=/home/ubuntu/rule1-app/backend
command=/home/ubuntu/rule1-app/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
user=ubuntu
autostart=true
autorestart=true
stderr_logfile=/var/log/rule1-api.err.log
stdout_logfile=/var/log/rule1-api.out.log
```

```bash
# Start the service
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start rule1-api
```

#### Frontend (React/Vite)

**Vercel (Easiest):**

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd frontend
vercel --prod
```

**Netlify:**

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Build and deploy
cd frontend
npm run build
netlify deploy --prod --dir=dist
```

**AWS S3 + CloudFront:**

```bash
# Build the app
cd frontend
npm run build

# Upload to S3
aws s3 sync dist/ s3://your-bucket-name --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

## Database Setup

### PostgreSQL Schema

Create a migration file or run directly:

```sql
CREATE TABLE analyses (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    meaning_score INTEGER CHECK (meaning_score >= 1 AND meaning_score <= 5),
    moat_score INTEGER CHECK (moat_score >= 1 AND moat_score <= 5),
    management_score INTEGER CHECK (management_score >= 1 AND management_score <= 5),
    margin_score INTEGER CHECK (margin_score >= 1 AND margin_score <= 5),
    overall_score DECIMAL(3,2),
    recommendation VARCHAR(50),
    user_notes TEXT
);

CREATE INDEX idx_analyses_symbol ON analyses(symbol);
CREATE INDEX idx_analyses_created_at ON analyses(created_at);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

CREATE TABLE watchlists (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    symbol VARCHAR(10) NOT NULL,
    target_price DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Database Migrations

Update `backend/main.py` to use PostgreSQL:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

## Environment Configuration

### Production Environment Variables

**Backend (.env):**
```env
# API Keys
ALPHA_VANTAGE_KEY=your_production_key

# Database
DATABASE_URL=postgresql://user:password@host:5432/rule1_investing

# Security
SECRET_KEY=your_very_secret_key_here
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
```

**Frontend (.env.production):**
```env
VITE_API_URL=https://api.yourdomain.com
VITE_ENV=production
```

## Nginx Configuration

Create `nginx.conf`:

```nginx
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:3000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    # API requests
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## SSL Certificate

### Using Let's Encrypt:

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal is configured by default
sudo certbot renew --dry-run
```

## Monitoring & Logging

### Backend Logging

Add to `main.py`:

```python
import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('api.log', maxBytes=10000000, backupCount=5),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### Application Monitoring

**Sentry Integration:**

```bash
pip install sentry-sdk
```

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
)
```

### Health Checks

Add to `main.py`:

```python
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers"""
    try:
        # Check database connection
        # Check external API availability
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

## Performance Optimization

### Backend Caching

```python
from functools import lru_cache
from cachetools import TTLCache

cache = TTLCache(maxsize=1000, ttl=3600)

@lru_cache(maxsize=128)
def cached_function(param):
    # Expensive operation
    pass
```

### Frontend Optimization

1. Enable code splitting
2. Lazy load components
3. Use service workers for caching
4. Optimize images
5. Enable gzip compression

```javascript
// vite.config.js
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          motion: ['framer-motion'],
        },
      },
    },
  },
});
```

## Backup Strategy

### Database Backups

```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -U postgres rule1_investing > "$BACKUP_DIR/backup_$DATE.sql"

# Keep only last 30 days
find $BACKUP_DIR -name "backup_*.sql" -mtime +30 -delete
```

### Automated Backups

Add to crontab:
```bash
0 2 * * * /path/to/backup-script.sh
```

## Scaling Considerations

### Horizontal Scaling

- Use load balancer (AWS ELB, Nginx)
- Deploy multiple backend instances
- Use Redis for shared caching
- Implement database read replicas

### Vertical Scaling

- Increase server resources
- Optimize database queries
- Use connection pooling
- Implement request queueing

## Monitoring Tools

- **Uptime**: UptimeRobot, Pingdom
- **APM**: New Relic, DataDog
- **Logs**: ELK Stack, Papertrail
- **Errors**: Sentry, Rollbar

## Security Checklist

- [ ] Enable HTTPS everywhere
- [ ] Implement rate limiting
- [ ] Use environment variables for secrets
- [ ] Enable CORS properly
- [ ] Sanitize user inputs
- [ ] Keep dependencies updated
- [ ] Use strong passwords for database
- [ ] Enable firewall rules
- [ ] Regular security audits
- [ ] Implement authentication/authorization

## Post-Deployment

1. Test all API endpoints
2. Verify SSL certificate
3. Check error logging
4. Monitor performance metrics
5. Set up alerting
6. Document any issues
7. Create runbook for common tasks

---

For questions or issues, consult the main README or open a GitHub issue.
