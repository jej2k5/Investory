# Rule #1 Investing Platform

A modern, API-first web application for analyzing stocks using Phil Town's proven "Rule #1 Investing" methodology. Built with Python FastAPI backend and React frontend.

![Rule #1 Investing](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-cyan)
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
├── backend/           # Python FastAPI REST API
│   ├── main.py       # API server with all endpoints
│   ├── requirements.txt
│   └── .env.example
├── frontend/          # React + Tailwind + Framer Motion
│   ├── App.jsx       # Main application component
│   ├── main.jsx      # React entry point
│   ├── package.json
│   └── vite.config.js
└── docs/             # API documentation
```

## ✨ Features

### Backend (FastAPI)
- **RESTful API** with automatic OpenAPI documentation
- **Stock Data Aggregation** from Alpha Vantage
- **Growth Rate Calculations** (10-year CAGR for Big Five metrics)
- **Valuation Engine** (Sticker Price & Margin of Safety)
- **Moat Evaluation** (automated assessment)
- **Caching Layer** (reduce API calls, improve performance)
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

### Prerequisites
- Python 3.9+
- Node.js 18+
- Alpha Vantage API key (free at https://www.alphavantage.co/support/#api-key)

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
# Edit .env and add your Alpha Vantage API key
```

5. Start the server:
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

### Key Endpoints

#### `GET /api/stocks/{symbol}`
Fetch comprehensive stock data including:
- Company information
- Current metrics (price, EPS, P/E, ROE)
- 10-year growth rates (Book Value, EPS, Cash Flow, Sales, ROIC)
- Historical financial statements

**Example Response:**
```json
{
  "symbol": "AAPL",
  "company_name": "Apple Inc.",
  "sector": "Technology",
  "current_metrics": {
    "price": 175.50,
    "eps": 6.15,
    "pe_ratio": 28.5,
    "roe": 0.45
  },
  "growth_rates": {
    "book_value": 12.5,
    "eps": 15.2,
    "cash_flow": 13.8,
    "sales": 11.2,
    "roic": 18.5
  }
}
```

#### `POST /api/valuation`
Calculate Sticker Price and Margin of Safety.

**Request Body:**
```json
{
  "current_eps": 6.15,
  "growth_rate": 14.2,
  "pe_ratio": 28.5
}
```

**Query Parameters:**
- `current_price`: Current stock price

**Response:**
```json
{
  "sticker_price": 180.25,
  "mos_price": 90.13,
  "current_price": 175.50,
  "recommendation": "WAIT - Not enough margin",
  "discount_percentage": 97.4
}
```

#### `GET /api/moat/evaluate`
Evaluate if a company has a wide moat.

**Query Parameters:**
- `book_value`: 10-year CAGR (%)
- `eps`: 10-year CAGR (%)
- `cash_flow`: 10-year CAGR (%)
- `sales`: 10-year CAGR (%)
- `roic`: Return on Invested Capital (%)

**Response:**
```json
{
  "has_wide_moat": true,
  "average_growth_rate": 14.2,
  "passing_metrics": 5,
  "total_metrics": 5,
  "assessment": "PASS - Wide moat"
}
```

#### `POST /api/analyses`
Save a stock analysis with Four Ms scores.

**Request Body:**
```json
{
  "symbol": "AAPL",
  "meaning_score": 5,
  "moat_score": 5,
  "management_score": 4,
  "margin_score": 3,
  "user_notes": "Excellent company but slightly overvalued"
}
```

#### `GET /api/analyses`
List saved analyses with optional filtering.

**Query Parameters:**
- `symbol` (optional): Filter by stock symbol
- `limit` (optional): Max results (default: 10)

## 🎨 Design Philosophy

The frontend follows modern design principles:
- **Bold, Distinctive Aesthetics**: Gradient backgrounds, glassmorphism effects
- **Smooth Animations**: Framer Motion for delightful micro-interactions
- **Dark Theme**: Optimized for extended use
- **Accessible**: WCAG AA compliant color contrasts
- **Performance**: Optimized bundle size, lazy loading

## 🔧 Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation using Python type annotations
- **httpx**: Async HTTP client for API calls
- **python-dotenv**: Environment variable management
- **Uvicorn**: ASGI server

### Frontend
- **React 18**: UI library with hooks
- **Vite**: Next-generation frontend tooling
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Production-ready animation library
- **Lucide React**: Beautiful icon set

## 📊 Data Sources

- **Alpha Vantage**: Stock quotes, company overviews, financial statements
- Free tier: 5 API requests/minute, 500 requests/day
- Premium tier available for higher limits

## 🔐 Environment Variables

### Backend (.env)
```env
ALPHA_VANTAGE_KEY=your_api_key_here
API_HOST=0.0.0.0
API_PORT=8000
```

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

## 📈 Future Enhancements

- [ ] PostgreSQL database integration
- [ ] User authentication & authorization
- [ ] Watchlist functionality
- [ ] Portfolio tracking
- [ ] Email alerts for price targets
- [ ] Additional data sources (Yahoo Finance, IEX Cloud)
- [ ] Technical analysis charts
- [ ] PDF report generation
- [ ] Mobile app (React Native)

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Phil Town for the Rule #1 Investing methodology
- Alpha Vantage for providing free financial data API
- The FastAPI and React communities

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Remember**: Rule #1 - Don't lose money. Rule #2 - Don't forget Rule #1.
