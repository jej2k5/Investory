# Docker Compose V2 - Quick Reference

## ✅ You're Using the Modern Version!

This project uses **Docker Compose V2** - the current standard.

## 📋 Common Commands

### Starting & Stopping
```bash
# Start all services
docker compose up -d

# Start and rebuild
docker compose up -d --build

# Stop all services
docker compose down

# Stop and remove volumes (⚠️ deletes data)
docker compose down -v
```

### Viewing & Monitoring
```bash
# View running services
docker compose ps

# View logs (all services)
docker compose logs -f

# View logs (specific service)
docker compose logs -f backend
docker compose logs -f frontend

# Check resource usage
docker stats
```

### Building
```bash
# Build all images
docker compose build

# Build specific service
docker compose build backend

# Build without cache
docker compose build --no-cache
```

### Restarting
```bash
# Restart all services
docker compose restart

# Restart specific service
docker compose restart backend
```

### Executing Commands
```bash
# Run command in container
docker compose exec backend python init_db.py

# Open shell in container
docker compose exec backend sh
docker compose exec frontend sh

# Database shell
docker compose exec db psql -U postgres -d investory
```

### Production Deployment
```bash
# Use production compose file
docker compose -f compose.prod.yml up -d

# View production logs
docker compose -f compose.prod.yml logs -f

# Stop production
docker compose -f compose.prod.yml down
```

## 🆚 What Changed from V1?

| Old (V1) | New (V2) |
|----------|----------|
| `docker-compose up -d` | `docker compose up -d` |
| `docker-compose.yml` | `compose.yml` (both work) |
| Separate binary | Built into Docker CLI |

## 🔧 Troubleshooting

### "docker: 'compose' is not a docker command"

You're using Docker Compose V1. Options:

1. **Update Docker** (Recommended)
   ```bash
   # macOS/Windows: Update Docker Desktop
   # Linux: sudo apt-get install docker-ce docker-ce-cli
   ```

2. **Use old syntax temporarily**
   ```bash
   docker-compose up -d  # Will work with V1
   ```

3. **Create alias**
   ```bash
   alias dc='docker compose'
   dc up -d  # Shorter!
   ```

## 💡 Pro Tips

### Use Shorter Aliases
```bash
# Add to ~/.bashrc or ~/.zshrc
alias dc='docker compose'
alias dcu='docker compose up -d'
alias dcd='docker compose down'
alias dcl='docker compose logs -f'
alias dcp='docker compose ps'
alias dcb='docker compose build'

# Reload shell
source ~/.bashrc

# Now use:
dcu        # Start
dcd        # Stop
dcl        # Logs
```

### Makefile Commands (Even Easier!)
```bash
make up           # Start services
make down         # Stop services
make logs         # View logs
make restart      # Restart all
make build        # Build images
make clean        # Cleanup

make help         # See all commands
```

## 📚 Full Documentation

- **[DOCKER-README.md](DOCKER-README.md)** - Quick start guide
- **[docs/DOCKER.md](docs/DOCKER.md)** - Complete Docker documentation
- **[DOCKER-COMPOSE-V2.md](DOCKER-COMPOSE-V2.md)** - V2 migration guide
- **[DOCKER-TROUBLESHOOTING.md](DOCKER-TROUBLESHOOTING.md)** - Problem solving

## 🎯 Most Used Commands

```bash
# 1. Start everything
docker compose up -d

# 2. Check status
docker compose ps

# 3. View logs
docker compose logs -f

# 4. Restart a service
docker compose restart backend

# 5. Stop everything
docker compose down
```

## ✨ Modern Features

V2 includes:

- ✅ Faster builds and operations
- ✅ Better error messages
- ✅ Improved dependency handling
- ✅ Built-in to Docker CLI
- ✅ GPU support
- ✅ Better resource management

---

**Remember:** No hyphen! It's `docker compose` not `docker-compose` 🚀
