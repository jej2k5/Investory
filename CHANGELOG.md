# Changelog

All notable changes to Investory will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- User authentication with JWT
- Per-user watchlists and analyses
- Real-time price alerts via email/webhook
- Portfolio tracking and performance analytics
- Historical price charts

## [1.0.0] - 2026-02-17

### Added
- Initial open-source release of Investory
- FastAPI backend with comprehensive REST API
- PostgreSQL database for persistent storage
- React + Tailwind CSS frontend with Framer Motion animations
- Four Ms stock analysis framework implementation
- Automated growth rate calculations (10-year CAGR for Big Five metrics)
- Valuation engine (Sticker Price & Margin of Safety calculations)
- Alpha Vantage API integration with 1-hour caching
- Watchlist management with price tracking
- Analysis history and CRUD operations
- Interactive API documentation (Swagger UI & ReDoc)
- Docker Compose development environment
- Docker Compose production configuration with Nginx
- Comprehensive documentation in `/docs` folder
- Makefile with convenient development commands
- Database initialization and migration scripts
- Health checks and graceful shutdown handling
- Contributing guidelines and code of conduct
- MIT License

### Features
- **Stock Analysis**: Real-time stock data fetching and analysis
- **Four Ms Framework**: Systematic evaluation using Meaning, Moat, Management, and Margin of Safety
- **Growth Metrics**: Automatic calculation of Book Value, EPS, Cash Flow, Sales, and ROIC growth rates
- **Valuation Tools**: Intrinsic value calculation using Phil Town's methodology
- **Database Caching**: Intelligent 1-hour cache to minimize API calls
- **Responsive UI**: Modern, mobile-friendly interface with dark mode support
- **API-First**: Complete REST API with automatic documentation

### Technical Stack
- **Backend**: Python 3.9+, FastAPI 0.109, SQLAlchemy, PostgreSQL 14+
- **Frontend**: React 18.2, Vite, Tailwind CSS 3.4, Framer Motion
- **DevOps**: Docker, Docker Compose, Nginx
- **APIs**: Alpha Vantage for stock market data

### Documentation
- Complete API reference with endpoint examples
- Database schema documentation
- Docker usage and deployment guides
- Production deployment instructions
- Contributing guidelines
- Security policy

---

## Release Notes

### v1.0.0 - Initial Release

This is the first public release of Investory, marking the transition from a private project to an open-source platform. The project has been completely rebranded and hardened for community use.

**What's Included:**
- Production-ready stock analysis platform
- Self-hostable with Docker
- Complete documentation
- API-first architecture
- Modern, responsive UI

**Getting Started:**
```bash
git clone https://github.com/yourusername/investory.git
cd investory
cp .env.example .env
# Add your Alpha Vantage API key to .env
docker compose up -d
```

Visit http://localhost:3000 to start analyzing stocks!

---

[Unreleased]: https://github.com/yourusername/investory/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/yourusername/investory/releases/tag/v1.0.0
