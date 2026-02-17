# Investory - Quick Setup After Download

## 📥 You've Downloaded the Complete Project!

This archive contains a **production-ready stock analysis platform** with:
- ✅ Python FastAPI backend with PostgreSQL
- ✅ React frontend with modern UI
- ✅ Complete Docker setup
- ✅ GitHub Actions CI/CD
- ✅ Comprehensive documentation

## ⚠️ Important: Docker Compose V2

This project uses **Docker Compose V2** (the modern version):

```bash
docker compose up -d     # ✅ Correct (no hyphen)
docker-compose up -d     # ❌ Old syntax
```

**If you see "docker: 'compose' is not a docker command":**
- You need to update Docker to get Compose V2
- Or see [DOCKER-COMPOSE-V2.md](DOCKER-COMPOSE-V2.md) for migration help

## 🚀 Get Started in 3 Steps

### Step 1: Extract the Archive

```bash
# If you downloaded the .zip file:
unzip investory-complete.zip
cd investory

# If you downloaded the .tar.gz file:
tar -xzf investory.tar.gz
cd investory
```

### Step 2: Set Up Environment

```bash
# Copy environment file
cp .env.example .env

# Edit with your Alpha Vantage API key (get free key at https://alphavantage.co)
nano .env  # or use any text editor
```

### Step 3: Start the Application

**Option A: Using Docker (Recommended)**
```bash
# One command to start everything!
docker compose up -d

# Wait 30 seconds, then access:
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/api/docs
```

**Option B: Using Make (Even Easier)**
```bash
make dev
```

**Option C: Manual Setup**
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
python main.py

# Frontend (in new terminal)
cd frontend
npm install
npm run dev
```

## 🔐 First Login - Authentication

Investory includes a complete authentication system with role-based access control.

### Default Admin Credentials

On first startup, a default admin user is automatically created:

```
Username: admin
Password: admin123
```

**⚠️ IMPORTANT:** You **MUST** change this password on first login!

### Authentication Features

- ✅ JWT token-based authentication
- ✅ Forced password change for default admin
- ✅ Role-based access control (admin/user)
- ✅ Admin-only user registration
- ✅ Secure password hashing with bcrypt
- ✅ User management interface

### User Roles

**Admin Users Can:**
- Analyze stocks and manage watchlists
- Create new user accounts
- View all users
- Delete user accounts
- Change their own password

**Regular Users Can:**
- Analyze stocks and manage watchlists
- Change their own password

### First Time Login Flow

1. **Start the application** and visit http://localhost:3000
2. **Login** with default credentials (admin/admin123)
3. **Change password** - You'll be forced to change the default password
4. **Create additional users** (optional) - Navigate to "User Management" to add more users

### Managing Users (Admin Only)

```bash
# After logging in as admin, click "User Management" in the top nav
# You can:
# - Create new users with custom usernames and passwords
# - Assign admin or regular user roles
# - Delete users (except yourself)
# - View all user accounts and their status
```

### Security Notes

1. **Change the SECRET_KEY in production**
   ```bash
   # Generate a secure secret key:
   python -c "import secrets; print(secrets.token_urlsafe(32))"

   # Add to .env file:
   SECRET_KEY=your-generated-secret-key
   ```

2. **JWT tokens expire after 30 minutes** for security

3. **Passwords must be at least 8 characters**

4. **Only admins can register new users** - No public registration

## 📚 What's Included?

### Core Application
```
investory/
├── backend/           # FastAPI + PostgreSQL backend
│   ├── main.py       # API server (622 lines)
│   ├── models.py     # Database models
│   ├── database.py   # DB configuration
│   ├── schemas.py    # Request/response schemas
│   └── Dockerfile    # Backend container
│
├── frontend/          # React + Tailwind frontend
│   ├── App.jsx       # Main application (650+ lines)
│   ├── Dockerfile    # Frontend container
│   └── nginx.conf    # Production web server
│
├── docker compose.yml          # Development stack
├── docker compose.prod.yml     # Production stack
└── Makefile                    # Convenient commands
```

### GitHub Actions CI/CD
```
.github/
├── workflows/
│   ├── ci.yml            # Testing & linting
│   ├── docker-build.yml  # Image building
│   └── release.yml       # Release automation
├── ISSUE_TEMPLATE/       # Bug & feature templates
├── dependabot.yml        # Dependency updates
└── pull_request_template.md
```

### Documentation
```
docs/
├── API.md                # Complete API reference
├── DATABASE.md           # PostgreSQL setup guide
├── DEPLOYMENT.md         # Production deployment
├── DOCKER.md            # Docker documentation
└── GITHUB-ACTIONS.md    # CI/CD guide
```

## 🎯 Next Steps

### 1. Test the Application

```bash
# Search for a stock
# Try: AAPL, MSFT, GOOGL

# The app will:
# ✅ Fetch real-time data
# ✅ Calculate growth rates
# ✅ Determine intrinsic value
# ✅ Save your analyses
```

### 2. Explore Features

- **Stock Analysis** - Four Ms framework evaluation
- **Valuation Calculator** - Sticker Price & Margin of Safety
- **Analysis History** - All analyses saved in PostgreSQL
- **API Documentation** - Interactive Swagger UI
- **Database UI** - pgAdmin (enable with `--profile tools`)

### 3. Deploy to Production

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for:
- Docker deployment
- Cloud platforms (AWS, GCP, Azure)
- SSL configuration
- Monitoring setup

### 4. Publish to GitHub

```bash
# Create new repository on GitHub, then:
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/investory.git
git push -u origin main

# GitHub Actions will automatically:
# ✅ Run tests
# ✅ Build Docker images
# ✅ Push to GitHub Container Registry
```

## 🔧 Common Commands

### Using Make (Easiest)
```bash
make help          # Show all commands
make up            # Start services
make down          # Stop services
make logs          # View logs
make restart       # Restart all
make db-backup     # Backup database
make clean         # Cleanup
```

### Using Docker Compose
```bash
docker compose up -d              # Start
docker compose down               # Stop
docker compose logs -f            # Logs
docker compose ps                 # Status
docker compose restart backend    # Restart service
```

### Manual Commands
```bash
# Backend
cd backend
python main.py

# Frontend
cd frontend
npm run dev

# Database
docker run -d --name postgres -p 5432:5432 \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=investory \
  postgres:14-alpine
```

## 📖 Important Files to Read

1. **README.md** - Main documentation
2. **DOCKER-README.md** - Docker quick start
3. **GITHUB-ACTIONS-QUICKSTART.md** - CI/CD guide
4. **CONTRIBUTING.md** - How to contribute
5. **docs/DATABASE.md** - Database setup

## 🐛 Troubleshooting

### Port Already in Use?
```bash
# Change ports in .env file:
BACKEND_PORT=8001
FRONTEND_PORT=3001
DB_PORT=5433
```

### Database Connection Error?
```bash
# Ensure PostgreSQL is running:
docker compose up -d db

# Or start with full stack:
docker compose up -d
```

### Images Not Building?
```bash
# Clear Docker cache:
docker system prune -a

# Rebuild:
docker compose build --no-cache
```

## 🎓 Learning Resources

### Included Documentation
- Full API reference with examples
- Database schema documentation
- Docker deployment guides
- GitHub Actions workflows
- Contributing guidelines

### External Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 🌟 Features Overview

### Backend
- RESTful API with automatic OpenAPI docs
- PostgreSQL database with SQLAlchemy ORM
- Stock data from Alpha Vantage
- 10-year growth rate calculations
- Valuation engine (Sticker Price)
- Caching layer (1-hour TTL)
- CRUD operations for analyses
- Watchlist management

### Frontend
- Modern React with hooks
- Framer Motion animations
- Tailwind CSS styling
- Real-time stock search
- Interactive Four Ms scoring
- Visual analytics
- Responsive design

### DevOps
- Docker containerization
- Multi-stage builds
- Health checks
- Auto-restart
- GitHub Actions CI/CD
- Automated testing
- Security scanning
- Dependency updates

## 💡 Pro Tips

1. **Get Your API Key First**
   - Visit https://www.alphavantage.co/support/#api-key
   - Free tier: 5 requests/min, 500/day
   - Add to `.env` file

2. **Use Docker for Development**
   - Consistent environment
   - No dependency conflicts
   - One-command setup

3. **Enable pgAdmin for Database Management**
   ```bash
   docker compose --profile tools up -d
   # Access at http://localhost:5050
   ```

4. **Read the Docs**
   - Everything is documented
   - Examples included
   - Troubleshooting guides

5. **Join GitHub Discussions**
   - Ask questions
   - Share feedback
   - Contribute improvements

## 🚀 Ready to Start!

```bash
# Quick start:
make dev

# Or manually:
docker compose up -d

# Then visit:
# http://localhost:3000
```

## 📞 Need Help?

1. Check documentation in `docs/` folder
2. Review troubleshooting section above
3. Check GitHub Issues for similar problems
4. Open a new issue with details

## 🎉 You're All Set!

Investory is ready to help you analyze stocks using Phil Town's proven methodology.

**Invest smarter. Track what matters.**

---

**Project Stats:**
- 44 total files
- 15,000+ lines of code
- Full-stack application
- Production-ready
- Enterprise CI/CD
- Comprehensive docs

Enjoy! 📈
