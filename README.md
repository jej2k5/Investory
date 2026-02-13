# Rule #1 Investing Platform

A modern, API-first web application for analyzing stocks using Phil Town's proven "Rule #1 Investing" methodology. Built with Python FastAPI backend, PostgreSQL database, and React frontend.

![Rule #1 Investing](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-cyan)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue)
![React](https://img.shields.io/badge/react-18.2-purple)

## 🎯 Overview

This platform helps investors evaluate stocks using the Four Ms framework:
- **Meaning**: Does the business have personal meaning to you?
- **Moat**: Does it have a durable competitive advantage?
- **Management**: Is leadership owner-oriented with integrity?
- **Margin of Safety**: Can you buy it at 50% of intrinsic value?

## 🏗️ Architecture

```
rule1-app/
├── backend/           # Python FastAPI REST API + PostgreSQL
│   ├── main.py       # API server with all endpoints
│   ├── models.py     # SQLAlchemy database models
│   ├── database.py   # Database configuration
│   ├── schemas.py    # Pydantic request/response schemas
│   ├── init_db.py    # Database initialization script
│   ├── requirements.txt
│   └── .env.example
├── frontend/          # React + Tailwind + Framer Motion
│   ├── App.jsx       # Main application component
│   ├── main.jsx      # React entry point
│   ├── package.json
│   └── vite.config.js
└── docs/             # Documentation
    ├── API.md        # API reference
    ├── DATABASE.md   # PostgreSQL setup guide
    └── DEPLOYMENT.md # Production deployment
```

## ✨ Features

### Backend (FastAPI + PostgreSQL)
- **RESTful API** with automatic OpenAPI documentation
- **PostgreSQL Database** for persistent storage
- **Stock Data Aggregation** from Alpha Vantage
- **Database Caching** (1-hour TTL for stock data)
- **Growth Rate Calculations** (10-year CAGR for Big Five metrics)
- **Valuation Engine** (Sticker Price & Margin of Safety)
- **Moat Evaluation** (automated assessment)
- **Analysis Management** (CRUD operations with history)
- **Watchlist Feature** (track stocks with target prices)
- **Statistics & Analytics** (analysis trends and insights)
- **CORS Support** (seamless frontend integration)

### Frontend (React)
- **Modern UI/UX** with Framer Motion animations
- **Distinctive Design** avoiding generic AI aesthetics
- **Real-time Stock Search**
- **Interactive Four Ms Scoring**
- **Visual Growth Rate Analysis**
- **Automatic Valuation Calculations**
- **Responsive Design** (mobile-friendly)

## 🚀 Quick Start

### Option 1: Docker (Recommended) 🐳

The fastest way to get started:

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Add your Alpha Vantage API key to .env
nano .env

# 3. Start everything!
docker compose up -d

# 4. Access the application
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/api/docs
```

See [DOCKER-README.md](DOCKER-README.md) for details.

### Option 2: Manual Setup

#### Prerequisites
- Python 3.9+
- PostgreSQL 14+
- Node.js 18+
- Alpha Vantage API key (free at https://www.alphavantage.co/support/#api-key)

### Database Setup

**Option 1: Docker (Recommended)**
```bash
docker run -d \
  --name rule1-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=rule1_investing \
  -p 5432:5432 \
  postgres:14-alpine
```

**Option 2: Local PostgreSQL**
```bash
# macOS
brew install postgresql@14
brew services start postgresql@14
createdb rule1_investing

# Ubuntu/Debian
sudo apt install postgresql
sudo systemctl start postgresql
sudo -u postgres createdb rule1_investing
```

See [docs/DATABASE.md](docs/DATABASE.md) for detailed setup instructions.

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env and add your credentials:
# - ALPHA_VANTAGE_KEY=your_api_key_here
# - DATABASE_URL=postgresql://postgres:postgres@localhost:5432/rule1_investing
```

5. Initialize database:
```bash
python init_db.py
```

6. Start the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

See [docs/API.md](docs/API.md) for complete API reference.

## 🗄️ Database Schema

### Tables
- **users**: User accounts (for future auth)
- **analyses**: Stock analyses with Four Ms scores
- **watchlists**: User watchlist with target prices
- **stock_cache**: Cached stock data (1-hour TTL)
- **api_usage**: API usage tracking

See [docs/DATABASE.md](docs/DATABASE.md) for detailed schema documentation.

## 🔧 Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **PostgreSQL**: Robust relational database
- **Pydantic**: Data validation using type hints
- **httpx**: Async HTTP client
- **Uvicorn**: ASGI server

### Frontend
- **React 18**: UI library with hooks
- **Vite**: Next-generation frontend tooling
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Production-ready animation library
- **Lucide React**: Beautiful icon set

## 📊 Key Features Explained

### Stock Data Caching
Stock data is cached in PostgreSQL with a 1-hour TTL to:
- Reduce API calls to Alpha Vantage
- Improve response times
- Stay within free tier rate limits

### Analysis History
All analyses are saved to the database with:
- Four Ms scores
- Financial metrics snapshot
- Growth rates at time of analysis
- Calculated recommendations
- User notes

### Watchlist
Track stocks you're interested in:
- Set target buy/sell prices
- Enable price alerts
- Add personal notes
- View all watched stocks

## 🚀 Production Deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for:
- Docker deployment
- PostgreSQL configuration
- SSL setup
- Monitoring & logging
- Backup strategies

## 🔐 Environment Variables

### Backend (.env)
```env
ALPHA_VANTAGE_KEY=your_api_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/rule1_investing
API_HOST=0.0.0.0
API_PORT=8000
```

## 📈 Future Enhancements

- [ ] User authentication & authorization (JWT)
- [ ] Email price alerts
- [ ] Portfolio tracking
- [ ] Additional data sources (Yahoo Finance, IEX)
- [ ] Technical analysis charts
- [ ] PDF report generation
- [ ] Mobile app (React Native)
- [ ] Real-time price updates (WebSockets)
- [ ] Social features (share analyses)

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Phil Town for the Rule #1 Investing methodology
- Alpha Vantage for financial data API
- The FastAPI, React, and PostgreSQL communities

## 📧 Support

For questions or issues:
- Open a GitHub issue
- Check [docs/](docs/) for detailed guides
- Review API documentation at `/api/docs`

---

**Remember**: Rule #1 - Don't lose money. Rule #2 - Don't forget Rule #1.
