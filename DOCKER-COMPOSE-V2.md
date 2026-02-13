# Docker Compose V2 Migration Guide

This project now uses **Docker Compose V2** syntax (the modern version).

## 📌 Key Changes

### Command Syntax

**Old (V1):**
```bash
docker-compose up -d
docker-compose down
docker-compose logs -f
```

**New (V2) - What we use now:**
```bash
docker compose up -d
docker compose down
docker compose logs -f
```

Notice: **No hyphen** between `docker` and `compose`

### File Names

**Old:**
- `docker-compose.yml`
- `docker-compose.prod.yml`

**New:**
- `compose.yml` (recommended)
- `compose.prod.yml`

Both naming conventions work, but `compose.yml` is the modern standard.

## ✅ Check Your Version

```bash
# Check if you have Docker Compose V2
docker compose version

# Should show something like:
# Docker Compose version v2.x.x
```

## 🔄 If You Have V1 (Legacy)

### Option 1: Install Docker Compose V2 (Recommended)

**On macOS/Windows:**
- Docker Desktop already includes V2
- Just update Docker Desktop to latest version

**On Linux:**
```bash
# Remove old docker-compose
sudo rm /usr/local/bin/docker-compose

# Docker Compose V2 comes with Docker CLI
# Just update Docker to latest version
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io

# Verify
docker compose version
```

### Option 2: Use Compatibility Shim

If you must use the old syntax, create an alias:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias docker-compose='docker compose'

# Reload shell
source ~/.bashrc
```

### Option 3: Revert File Names (Not Recommended)

```bash
# In project directory
mv compose.yml docker-compose.yml
mv compose.prod.yml docker-compose.prod.yml

# Then use old commands
docker-compose up -d
```

## 📚 What Works in This Project

All documentation and scripts use the **V2 syntax**:

✅ `docker compose up -d`
✅ `docker compose down`
✅ `docker compose build`
✅ `docker compose logs -f`
✅ `make up` (uses docker compose internally)

## 🆕 V2 Advantages

1. **Integrated** - Part of Docker CLI, not separate binary
2. **Faster** - Better performance
3. **Better** - Improved error messages
4. **Standard** - Official Docker recommendation
5. **Features** - New capabilities and improvements

## 🔍 Troubleshooting

### "docker: 'compose' is not a docker command"

**You have Docker Compose V1 only**

**Fix:**
```bash
# Check Docker version
docker --version

# Update Docker (includes Compose V2)
# macOS/Windows: Update Docker Desktop
# Linux: Follow installation guide above
```

### "compose.yml not found"

**You might be looking for docker-compose.yml**

**Fix:**
```bash
# Check which file you have
ls -la *.yml

# If you have docker-compose.yml, either:
# 1. Rename it (recommended):
mv docker-compose.yml compose.yml

# 2. Or specify the file:
docker compose -f docker-compose.yml up -d
```

### Commands still don't work

**Create an alias as temporary fix:**

```bash
# Add to shell config
echo "alias docker-compose='docker compose'" >> ~/.bashrc
source ~/.bashrc

# Now old commands work
docker-compose up -d
```

## 📖 Quick Reference

| Task | V2 Command |
|------|------------|
| Start | `docker compose up -d` |
| Stop | `docker compose down` |
| Build | `docker compose build` |
| Logs | `docker compose logs -f` |
| Status | `docker compose ps` |
| Restart | `docker compose restart` |
| Execute | `docker compose exec SERVICE CMD` |

## 🎯 Best Practices

1. **Use V2** - It's the future of Docker Compose
2. **No hyphen** - Modern syntax is `docker compose`
3. **Use compose.yml** - Modern filename convention
4. **Update regularly** - Keep Docker up to date

## 📚 Official Documentation

- [Docker Compose V2](https://docs.docker.com/compose/compose-v2/)
- [Migrate to V2](https://docs.docker.com/compose/migrate/)
- [Install Docker Compose](https://docs.docker.com/compose/install/)

## ℹ️ Note for This Project

**All commands in this project use Docker Compose V2 syntax:**
- Documentation uses `docker compose` (no hyphen)
- File is named `compose.yml`
- Makefile uses modern commands

This ensures compatibility with modern Docker installations and follows current best practices.
