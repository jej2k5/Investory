# Investory API Documentation

## Base URL
```
http://localhost:8000/api
```

## Authentication
The API uses JWT bearer authentication for protected routes.

Include the access token from `POST /api/auth/login` in the `Authorization` header:

```bash
-H "Authorization: Bearer <token>"
```

Watchlist endpoints are authenticated and always scoped to the currently authenticated user.

## Rate Limiting
- Inherits Alpha Vantage's rate limits:
  - Free tier: 5 requests/minute, 500 requests/day
  - Caching reduces external API calls significantly


## MCP Integration

For agent-platform integrations, use the MCP service documented in [`docs/MCP.md`](./MCP.md). It exposes stock metrics, valuation, moat evaluation, and user-scoped watchlist workflows over MCP-compatible JSON-RPC transports.

## Endpoints

### Health Check

#### `GET /`
Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "service": "Investory API",
  "version": "1.0.0",
  "timestamp": "2024-02-13T10:30:00Z"
}
```

---

### Stock Data

#### `GET /api/stocks/{symbol}`
Fetch comprehensive stock data with growth rates and current metrics.

**Parameters:**
- `symbol` (path, required): Stock ticker symbol (e.g., "AAPL", "MSFT")

**Response:** `200 OK`
```json
{
  "symbol": "AAPL",
  "company_name": "Apple Inc.",
  "sector": "Technology",
  "industry": "Consumer Electronics",
  "description": "Apple Inc. designs, manufactures...",
  "current_metrics": {
    "price": 175.50,
    "eps": 6.15,
    "pe_ratio": 28.5,
    "book_value": 4.25,
    "dividend_yield": 0.0055,
    "roe": 0.45,
    "profit_margin": 0.25,
    "market_cap": 2750000000000
  },
  "growth_rates": {
    "book_value": 12.5,
    "eps": 15.2,
    "cash_flow": 13.8,
    "sales": 11.2,
    "roic": 18.5
  },
  "fetched_at": "2024-02-13T10:30:00Z"
}
```

**Errors:**
- `404 Not Found`: Stock symbol not found
- `500 Internal Server Error`: Error fetching data from external API

**Example:**
```bash
curl http://localhost:8000/api/stocks/AAPL
```

---

### Valuation

#### `POST /api/valuation`
Calculate Sticker Price and Margin of Safety using Rule #1 formula.

**Query Parameters:**
- `current_price` (required): Current stock price

**Request Body:**
```json
{
  "current_eps": 6.15,
  "growth_rate": 14.2,
  "pe_ratio": 28.5
}
```

**Response:** `200 OK`
```json
{
  "sticker_price": 180.25,
  "mos_price": 90.13,
  "current_price": 175.50,
  "recommendation": "WAIT - Not enough margin",
  "discount_percentage": 97.4
}
```

**Recommendation Logic:**
- `"BUY - On Sale!"`: Current price ≤ MOS price (50% discount)
- `"WAIT - Not enough margin"`: MOS price < Current price ≤ Sticker price
- `"AVOID - Overvalued"`: Current price > Sticker price

**Formula:**
1. Future EPS = Current EPS × (1 + Growth Rate)^10
2. Future Price = Future EPS × P/E Ratio
3. Sticker Price = Future Price ÷ (1.15)^10
4. MOS Price = Sticker Price × 0.5

**Example:**
```bash
curl -X POST "http://localhost:8000/api/valuation?current_price=175.50" \
  -H "Content-Type: application/json" \
  -d '{
    "current_eps": 6.15,
    "growth_rate": 14.2,
    "pe_ratio": 28.5
  }'
```

---

### Moat Evaluation

#### `GET /api/moat/evaluate`
Evaluate if a company has a wide moat based on the Big Five growth rates.

**Query Parameters (all required):**
- `book_value`: 10-year CAGR for book value per share (0-100)
- `eps`: 10-year CAGR for earnings per share (0-100)
- `cash_flow`: 10-year CAGR for operating cash flow (0-100)
- `sales`: 10-year CAGR for sales per share (0-100)
- `roic`: Return on invested capital (0-100)

**Response:** `200 OK`
```json
{
  "has_wide_moat": true,
  "average_growth_rate": 14.24,
  "rates": {
    "book_value": 12.5,
    "eps": 15.2,
    "cash_flow": 13.8,
    "sales": 11.2,
    "roic": 18.5
  },
  "passing_metrics": 5,
  "total_metrics": 5,
  "assessment": "PASS - Wide moat"
}
```

**Moat Criteria:**
- All five metrics must be ≥10% annually to pass
- Indicates durable competitive advantage

**Example:**
```bash
curl "http://localhost:8000/api/moat/evaluate?book_value=12.5&eps=15.2&cash_flow=13.8&sales=11.2&roic=18.5"
```

---

### Analyses

#### `POST /api/analyses`
Save a stock analysis with Four Ms scores.

**Request Body:**
```json
{
  "symbol": "AAPL",
  "user_notes": "Excellent company with strong moat",
  "meaning_score": 5,
  "moat_score": 5,
  "management_score": 4,
  "margin_score": 3
}
```

**Field Descriptions:**
- `symbol` (required): Stock ticker
- `user_notes` (optional): Personal notes about the analysis
- `meaning_score` (optional): 1-5, does it have meaning to you?
- `moat_score` (optional): 1-5, does it have a wide moat?
- `management_score` (optional): 1-5, is management excellent?
- `margin_score` (optional): 1-5, is there a margin of safety?

**Response:** `200 OK`
```json
{
  "id": 1,
  "symbol": "AAPL",
  "created_at": "2024-02-13T10:30:00Z",
  "updated_at": "2024-02-13T10:30:00Z",
  "meaning_score": 5,
  "moat_score": 5,
  "management_score": 4,
  "margin_score": 3,
  "overall_score": 4.25,
  "recommendation": "STRONG BUY"
}
```

**Overall Score Calculation:**
- Average of all non-zero scores
- Recommendation:
  - ≥4.0: "STRONG BUY"
  - ≥3.5: "BUY"
  - ≥3.0: "HOLD"
  - <3.0: "PASS"

**Example:**
```bash
curl -X POST http://localhost:8000/api/analyses \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "meaning_score": 5,
    "moat_score": 5,
    "management_score": 4,
    "margin_score": 3
  }'
```

#### `GET /api/analyses`
List saved analyses with optional filtering.

**Query Parameters:**
- `symbol` (optional): Filter by stock symbol
- `limit` (optional): Maximum results (1-100, default: 10)

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "symbol": "AAPL",
    "created_at": "2024-02-13T10:30:00Z",
    "updated_at": "2024-02-13T10:30:00Z",
    "meaning_score": 5,
    "moat_score": 5,
    "management_score": 4,
    "margin_score": 3,
    "overall_score": 4.25,
    "recommendation": "STRONG BUY"
  }
]
```

**Example:**
```bash
# Get all analyses
curl http://localhost:8000/api/analyses

# Get analyses for AAPL
curl "http://localhost:8000/api/analyses?symbol=AAPL"

# Get last 5 analyses
curl "http://localhost:8000/api/analyses?limit=5"
```

#### `GET /api/analyses/{analysis_id}`
Get a specific analysis by ID.

**Parameters:**
- `analysis_id` (path, required): Analysis ID

**Response:** `200 OK`
```json
{
  "id": 1,
  "symbol": "AAPL",
  "created_at": "2024-02-13T10:30:00Z",
  "updated_at": "2024-02-13T10:30:00Z",
  "meaning_score": 5,
  "moat_score": 5,
  "management_score": 4,
  "margin_score": 3,
  "overall_score": 4.25,
  "recommendation": "STRONG BUY"
}
```

**Errors:**
- `404 Not Found`: Analysis not found

**Example:**
```bash
curl http://localhost:8000/api/analyses/1
```


### Watchlist (Authenticated)

All watchlist endpoints require `Authorization: Bearer <token>` and only operate on the authenticated user's own items.

#### `POST /api/watchlist`
Add a stock to the authenticated user's watchlist.

#### `GET /api/watchlist`
List watchlist items for the authenticated user only.

#### `GET /api/watchlist/{item_id}`
Get one watchlist item owned by the authenticated user. Returns `404` if not found or not owned.

#### `PUT /api/watchlist/{item_id}`
Update one watchlist item owned by the authenticated user. Returns `404` if not found or not owned.

#### `DELETE /api/watchlist/{item_id}`
Delete one watchlist item owned by the authenticated user. Returns `404` if not found or not owned.

**Example:**
```bash
curl -X GET http://localhost:8000/api/watchlist \
  -H "Authorization: Bearer <token>"
```

---

## Error Responses

All endpoints may return the following error responses:

### `400 Bad Request`
```json
{
  "detail": "Error message describing what went wrong"
}
```

### `404 Not Found`
```json
{
  "detail": "Resource not found"
}
```

### `500 Internal Server Error`
```json
{
  "detail": "Internal server error message"
}
```

---

## Data Models

### StockData
```typescript
{
  symbol: string
  company_name: string
  sector: string | null
  industry: string | null
  description: string | null
  current_metrics: CurrentMetrics
  growth_rates: GrowthRates
  fetched_at: datetime
}
```

### CurrentMetrics
```typescript
{
  price: number
  eps: number
  pe_ratio: number
  book_value: number
  dividend_yield: number
  roe: number
  profit_margin: number
  market_cap: number
}
```

### GrowthRates
```typescript
{
  book_value: number  // 10-year CAGR %
  eps: number         // 10-year CAGR %
  cash_flow: number   // 10-year CAGR %
  sales: number       // 10-year CAGR %
  roic: number        // Current ROIC %
}
```

### ValuationOutput
```typescript
{
  sticker_price: number
  mos_price: number
  current_price: number
  recommendation: string
  discount_percentage: number
}
```

### AnalysisResponse
```typescript
{
  id: number
  symbol: string
  created_at: datetime
  updated_at: datetime
  meaning_score: number | null
  moat_score: number | null
  management_score: number | null
  margin_score: number | null
  overall_score: number
  recommendation: string
}
```

---

## Interactive Documentation

For interactive API documentation with the ability to test endpoints:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

Both interfaces are automatically generated from the FastAPI code and stay in sync with the implementation.
