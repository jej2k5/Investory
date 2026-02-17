# Investory

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-cyan)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue)
![React](https://img.shields.io/badge/react-18.2-purple)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**Invest smarter. Track what matters.**

Investory is an open-source stock analysis platform built around Phil Town's Four Ms investing framework. Self-hostable, API-first, and Docker-ready.

---

## 🎯 Overview

Investory helps investors evaluate stocks systematically using the proven Four Ms framework:

- 🎯 **Meaning**: Does the business have personal meaning to you?
- 🏰 **Moat**: Does it have a durable competitive advantage?
- 👔 **Management**: Is leadership owner-oriented with integrity?
- 💰 **Margin of Safety**: Can you buy it at 50% of intrinsic value?

Combined with automated financial analysis, growth rate calculations, and valuation tools, Investory makes fundamental analysis accessible and systematic.

---

## ✨ Features

**Backend (FastAPI + PostgreSQL)**
- RESTful API with automatic OpenAPI documentation
- PostgreSQL database for persistent storage
- Alpha Vantage integration with 1-hour caching
- Automated growth rate calculations (10-year CAGR)
- Valuation engine (Sticker Price & Margin of Safety)
- Four Ms scoring and recommendation system
- Watchlist management with price alerts

**Frontend (React + Tailwind CSS)**
- Modern, responsive UI with dark mode
- Real-time stock search and analysis
- Interactive Four Ms evaluation interface
- Visual growth rate charts and metrics
- Watchlist dashboard with tracking
- Framer Motion animations

**DevOps & Infrastructure**
- Docker Compose for local development
- Production-ready multi-container setup
- Nginx reverse proxy configuration
- Health checks and graceful shutdowns
- Database migration scripts

---

## 🏗️ Architecture

```
investory/
├── backend/              # Python FastAPI REST API
│   ├── main.py          # API server with all endpoints
│   ├── models.py        # SQLAlchemy database models
│   ├── database.py      # Database configuration
│   ├── schemas.py       # Pydantic request/response schemas
│   ├── init_db.py       # Database initialization
│   ├── requirements.txt
│   └── .env.example
├── frontend/            # React + Vite + Tailwind CSS
│   ├── src/
│   │   ├── App.jsx     # Main application component
│   │   └── main.jsx    # React entry point
│   ├── package.json
│   └── vite.config.js
├── docs/                # Documentation
│   ├── API.md          # API reference
│   ├── DATABASE.md     # Database schema
│   ├── DEPLOYMENT.md   # Production deployment guide
│   └── DOCKER.md       # Docker usage
├── compose.yml         # Development Docker Compose
├── compose.prod.yml    # Production Docker Compose
└── Makefile            # Common commands
```

**System Architecture:**
```
┌─────────────┐      ┌──────────────┐      ┌───────────────┐
│   React     │─────▶│   FastAPI    │─────▶│  PostgreSQL   │
│  Frontend   │      │   Backend    │      │   Database    │
└─────────────┘      └──────────────┘      └───────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │ Alpha Vantage│
                     │     API      │
                     └──────────────┘
```

---

## 🚀 Quick Start

Get Investory running in under 60 seconds:

```bash
# Clone the repository
git clone https://github.com/yourusername/investory.git
cd investory

# Copy environment file
cp .env.example .env

# Edit .env and add your Alpha Vantage API key (get one free at https://www.alphavantage.co)

# Start all services with Docker Compose
docker compose up -d

# View logs
docker compose logs -f
```

Access the application:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs

---

## 📦 Local Development Setup

### Prerequisites

- **Docker** (20.10+) and **Docker Compose** (2.0+)
- **Git**
- **Alpha Vantage API Key** (free at https://www.alphavantage.co/support/#api-key)

### Step-by-Step Installation

1. **Clone and navigate to the project:**
   ```bash
   git clone https://github.com/yourusername/investory.git
   cd investory
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and set your ALPHA_VANTAGE_KEY
   ```

3. **Build and start services:**
   ```bash
   docker compose up -d --build
   ```

4. **Initialize the database (first time only):**
   ```bash
   docker compose exec backend python init_db.py
   ```

5. **Verify installation:**
   ```bash
   curl http://localhost:8000/
   # Should return: {"status":"healthy","service":"Investory API",...}
   ```

### Development Workflow

```bash
# Start services
make up

# View logs
make logs

# Restart a service
make restart-backend

# Stop services
make down

# Run backend tests
make test-backend

# Access database shell
make shell-db
```

See the `Makefile` for all available commands.

---

## 📖 API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

Key endpoints:
- `GET /api/stocks/{symbol}` - Fetch stock data with growth rates
- `POST /api/valuation` - Calculate Sticker Price and MOS
- `POST /api/analyses` - Save Four Ms analysis
- `GET /api/analyses` - List saved analyses
- `POST /api/watchlist` - Add stock to watchlist
- `GET /api/watchlist` - Get all watchlist items

For detailed API documentation, see [docs/API.md](docs/API.md).

---

## 🗄️ Database

Investory uses PostgreSQL 14+ with the following tables:

- **users** - User accounts (future auth integration)
- **analyses** - Saved stock analyses with Four Ms scores
- **watchlist** - User watchlist with price alerts
- **stock_cache** - Cached Alpha Vantage API responses (1-hour TTL)
- **api_usage** - API call tracking and rate limiting

See [docs/DATABASE.md](docs/DATABASE.md) for schema details.

---

## 🚢 Production Deployment

Deploy Investory to production using the included production Docker Compose configuration:

```bash
# Use production compose file
docker compose -f compose.prod.yml up -d
```

Production features:
- Nginx reverse proxy with SSL support
- Multi-worker FastAPI backend
- Persistent volumes for database
- Health checks and auto-restart
- Optimized build for frontend

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment instructions including:
- VPS/cloud deployment
- SSL certificate setup
- Environment variable configuration
- Backup and restore procedures

---

## 🗺️ Roadmap

**v1.1 - Authentication & Multi-User**
- User authentication with JWT
- Per-user watchlists and analyses
- User preferences and settings

**v1.2 - Advanced Features**
- Portfolio tracking and performance
- Historical price charts
- Dividend tracking
- Real-time price alerts via email/webhook

**v1.3 - Enhanced Analysis**
- Industry comparison tools
- Competitor analysis
- Financial statement visualization
- Custom valuation models

**v2.0 - Platform Expansion**
- Mobile app (React Native)
- CSV/Excel import/export
- Integration with brokers (Alpaca, Interactive Brokers)
- Community-shared analyses

---

## 🤝 Contributing

We welcome contributions from the community! Whether it's:

- 🐛 Bug reports and fixes
- ✨ New features and enhancements
- 📖 Documentation improvements
- 🧪 Test coverage expansion

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Good First Issues**: Check out issues tagged with `good-first-issue` to get started!

---

## 📄 License

Investory is open-source software licensed under the [MIT License](LICENSE).

---

## 🙏 Acknowledgments

- **Phil Town** - For the Four Ms investing framework
- **Alpha Vantage** - For providing free stock market data API
- **FastAPI** - For the excellent Python web framework
- **React** - For the powerful frontend library

---

## 📞 Support

- **Documentation**: See the `/docs` folder
- **Issues**: https://github.com/yourusername/investory/issues
- **Discussions**: https://github.com/yourusername/investory/discussions

---

**Built with ❤️ by the open-source community**
