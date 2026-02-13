# Docker Build Troubleshooting Guide

## Common Build Errors and Solutions

### Frontend Build Error: "vite: not found"

**Error:**
```
> vite build
sh: vite: not found
```

**Cause:** Development dependencies not installed (vite is a devDependency)

**Solution 1: Use npm install instead of npm ci --only=production**
```dockerfile
# In frontend/Dockerfile, change:
RUN npm ci --only=production
# To:
RUN npm install
```

**Solution 2: Build locally first**
```bash
cd frontend
npm install
npm run build
cd ..
docker compose build frontend
```

**Solution 3: Use the updated Dockerfile** (already fixed in latest version)

---

### Backend Build Error: "pip install failed"

**Error:**
```
ERROR: Could not install packages
```

**Solution 1: Clear Docker cache**
```bash
docker builder prune -a
docker compose build --no-cache backend
```

**Solution 2: Check requirements.txt**
```bash
cd backend
cat requirements.txt
# Ensure all packages are valid
```

**Solution 3: Build with verbose output**
```bash
docker compose build --progress=plain backend
```

---

### PostgreSQL Connection Error

**Error:**
```
psycopg2.OperationalError: could not connect to server
```

**Solution 1: Wait for database to be ready**
```bash
# Add sleep in docker compose command
command: >
  sh -c "
    sleep 10 &&
    python init_db.py &&
    uvicorn main:app --host 0.0.0.0 --port 8000
  "
```

**Solution 2: Check database is running**
```bash
docker compose ps db
docker compose logs db
```

**Solution 3: Verify DATABASE_URL in .env**
```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/rule1_investing
```

---

### Port Already in Use

**Error:**
```
Error: Bind for 0.0.0.0:3000 failed: port is already allocated
```

**Solution 1: Change port in .env**
```env
FRONTEND_PORT=3001
BACKEND_PORT=8001
```

**Solution 2: Stop conflicting service**
```bash
# Find what's using the port
lsof -i :3000

# Kill the process
kill -9 PID
```

**Solution 3: Use different ports in docker compose.yml**
```yaml
ports:
  - "3001:80"  # Map host 3001 to container 80
```

---

### Build Takes Too Long

**Symptom:** Build runs for 5+ minutes

**Solution 1: Use layer caching**
```bash
# Build with cache
docker compose build

# Subsequent builds will be much faster
```

**Solution 2: Ensure .dockerignore is present**
```bash
# Check if .dockerignore exists
cat frontend/.dockerignore
cat backend/.dockerignore
```

**Solution 3: Use buildkit**
```bash
# Enable BuildKit for faster builds
export DOCKER_BUILDKIT=1
docker compose build
```

---

### "No space left on device"

**Error:**
```
Error: failed to copy: no space left on device
```

**Solution 1: Clean Docker system**
```bash
docker system prune -a --volumes
```

**Solution 2: Remove unused images**
```bash
docker image prune -a
```

**Solution 3: Check disk space**
```bash
df -h
```

---

### Package-lock.json Missing

**Error:**
```
npm ERR! Cannot read property 'match' of undefined
```

**Solution 1: Generate package-lock.json**
```bash
cd frontend
npm install
# This creates package-lock.json
```

**Solution 2: Use npm install instead of npm ci**
```dockerfile
# Change in Dockerfile:
RUN npm ci
# To:
RUN npm install
```

---

### Database Initialization Fails

**Error:**
```
Database rule1_investing does not exist
```

**Solution 1: Wait for database startup**
```bash
# Ensure db service starts first
docker compose up -d db
sleep 10
docker compose up -d backend
```

**Solution 2: Manually initialize**
```bash
docker compose exec backend python init_db.py
```

**Solution 3: Check logs**
```bash
docker compose logs db
docker compose logs backend
```

---

## Quick Fixes

### Reset Everything
```bash
# Stop all containers
docker compose down -v

# Remove all images
docker rmi $(docker images -q rule1-app*)

# Clean system
docker system prune -a

# Rebuild from scratch
docker compose build --no-cache
docker compose up -d
```

### Fresh Start
```bash
# Complete clean slate
docker compose down -v
rm -rf frontend/node_modules
rm -rf backend/__pycache__
docker compose build --no-cache
docker compose up -d
```

### Rebuild Single Service
```bash
# Rebuild only backend
docker compose build --no-cache backend
docker compose up -d backend

# Rebuild only frontend
docker compose build --no-cache frontend
docker compose up -d frontend
```

---

## Debug Commands

### View Build Logs
```bash
# Show build output
docker compose build --progress=plain

# View container logs
docker compose logs -f backend
docker compose logs -f frontend
```

### Check Service Health
```bash
# Check all services
docker compose ps

# Check specific service
docker inspect $(docker compose ps -q backend) | grep Health
```

### Enter Running Container
```bash
# Backend shell
docker compose exec backend sh

# Frontend shell (nginx)
docker compose exec frontend sh

# Database shell
docker compose exec db psql -U postgres -d rule1_investing
```

### Test Services Manually
```bash
# Test backend
curl http://localhost:8000/

# Test frontend
curl http://localhost:3000/

# Test database
docker compose exec db pg_isready -U postgres
```

---

## Prevention Tips

1. **Always use .dockerignore**
   - Speeds up builds
   - Reduces image size
   - Prevents unnecessary file copies

2. **Order Dockerfile commands correctly**
   - Put least-changing commands first
   - Dependencies before code
   - Enables layer caching

3. **Use specific versions**
   ```dockerfile
   FROM python:3.11-slim  # Good
   FROM python:latest     # Bad
   ```

4. **Test locally first**
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt
   python main.py
   
   # Frontend
   cd frontend
   npm install
   npm run build
   ```

5. **Check .env configuration**
   ```bash
   cat .env
   # Ensure all required variables are set
   ```

---

## Still Having Issues?

1. **Check the logs:**
   ```bash
   docker compose logs -f
   ```

2. **Verify Docker is running:**
   ```bash
   docker --version
   docker compose --version
   ```

3. **Check available resources:**
   ```bash
   docker stats
   df -h
   ```

4. **Review documentation:**
   - README.md
   - DOCKER-README.md
   - docs/DOCKER.md

5. **Open an issue:**
   - Provide error message
   - Include Docker version
   - Show docker compose logs output

---

## Quick Reference

| Issue | Command |
|-------|---------|
| Clean everything | `docker system prune -a --volumes` |
| Rebuild service | `docker compose build --no-cache SERVICE` |
| View logs | `docker compose logs -f SERVICE` |
| Restart service | `docker compose restart SERVICE` |
| Check status | `docker compose ps` |
| Enter container | `docker compose exec SERVICE sh` |
| Fresh start | `docker compose down -v && docker compose up -d --build` |
