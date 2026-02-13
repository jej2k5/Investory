"""
Rule #1 Investing API - FastAPI Backend
Modern, API-first architecture for stock analysis with PostgreSQL
"""

import asyncio
import os
from datetime import datetime, timedelta
from typing import List, Optional

import httpx
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

# Import database and models
from database import get_db, init_db
from models import Analysis, StockCache, User, Watchlist
from schemas import (
    AnalysisCreate,
    AnalysisResponse,
    AnalysisStats,
    AnalysisUpdate,
    CurrentMetrics,
    GrowthRates,
    MoatEvaluation,
    StockData,
    ValuationInput,
    ValuationOutput,
    WatchlistCreate,
    WatchlistResponse,
    WatchlistUpdate,
)

load_dotenv()

# Initialize database on startup
try:
    init_db()
    print("✅ Database initialized successfully")
except Exception as e:
    print(f"⚠️  Database initialization warning: {e}")

app = FastAPI(
    title="Rule #1 Investing API",
    description="API for analyzing stocks using Phil Town's Four Ms framework with PostgreSQL storage",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== UTILITIES ====================


class AlphaVantageClient:
    """Client for Alpha Vantage API with database caching"""

    def __init__(self):
        self.api_key = os.getenv("ALPHA_VANTAGE_KEY", "demo")
        self.base_url = "https://www.alphavantage.co/query"
        self.cache_ttl = timedelta(hours=1)

    async def fetch(self, function: str, symbol: str, db: Session = None) -> dict:
        """Fetch data from Alpha Vantage"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    self.base_url,
                    params={
                        "function": function,
                        "symbol": symbol,
                        "apikey": self.api_key,
                    },
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error fetching from Alpha Vantage: {str(e)}")


# Global client instance
alpha_vantage = AlphaVantageClient()


def calculate_cagr(start_value: float, end_value: float, years: int) -> float:
    """Calculate Compound Annual Growth Rate"""
    if start_value <= 0 or years <= 0:
        return 0.0
    try:
        return ((end_value / start_value) ** (1 / years) - 1) * 100
    except:
        return 0.0


def calculate_growth_rates(income_data: List[dict], balance_data: List[dict], cash_flow_data: List[dict]) -> GrowthRates:
    """Calculate 10-year CAGR for various metrics"""
    rates = GrowthRates()

    try:
        # Revenue/Sales Growth
        if len(income_data) >= 2:
            latest_revenue = float(income_data[0].get("totalRevenue", 0))
            oldest_revenue = float(income_data[min(9, len(income_data) - 1)].get("totalRevenue", 0))
            years = min(10, len(income_data))
            rates.sales = calculate_cagr(oldest_revenue, latest_revenue, years)

        # EPS Growth (using net income as proxy)
        if len(income_data) >= 2:
            latest_income = float(income_data[0].get("netIncome", 0))
            oldest_income = float(income_data[min(9, len(income_data) - 1)].get("netIncome", 0))
            years = min(10, len(income_data))
            rates.eps = calculate_cagr(oldest_income, latest_income, years)

        # Book Value Growth
        if len(balance_data) >= 2:
            latest_equity = float(balance_data[0].get("totalShareholderEquity", 0))
            oldest_equity = float(balance_data[min(9, len(balance_data) - 1)].get("totalShareholderEquity", 0))
            years = min(10, len(balance_data))
            rates.book_value = calculate_cagr(oldest_equity, latest_equity, years)

        # Cash Flow Growth
        if len(cash_flow_data) >= 2:
            latest_cf = float(cash_flow_data[0].get("operatingCashflow", 0))
            oldest_cf = float(cash_flow_data[min(9, len(cash_flow_data) - 1)].get("operatingCashflow", 0))
            years = min(10, len(cash_flow_data))
            rates.cash_flow = calculate_cagr(oldest_cf, latest_cf, years)

        # ROIC (simplified using ROE as proxy)
        if len(income_data) >= 1 and len(balance_data) >= 1:
            net_income = float(income_data[0].get("netIncome", 0))
            equity = float(balance_data[0].get("totalShareholderEquity", 0))
            if equity > 0:
                rates.roic = (net_income / equity) * 100

    except Exception as e:
        print(f"Error calculating growth rates: {e}")

    return rates


def calculate_sticker_price(current_eps: float, growth_rate: float, pe_ratio: float) -> float:
    """Calculate intrinsic value (Sticker Price) using Rule #1 formula"""
    try:
        future_eps = current_eps * ((1 + growth_rate / 100) ** 10)
        future_price = future_eps * pe_ratio
        sticker_price = future_price / (1.15**10)
        return round(sticker_price, 2)
    except:
        return 0.0


def calculate_overall_score(
    meaning: Optional[int], moat: Optional[int], management: Optional[int], margin: Optional[int]
) -> float:
    """Calculate overall score from Four Ms"""
    scores = [s for s in [meaning, moat, management, margin] if s is not None and s > 0]
    if not scores:
        return 0.0
    return round(sum(scores) / len(scores), 2)


def get_recommendation(overall_score: float) -> str:
    """Get recommendation based on overall score"""
    if overall_score >= 4.0:
        return "STRONG BUY"
    elif overall_score >= 3.5:
        return "BUY"
    elif overall_score >= 3.0:
        return "HOLD"
    else:
        return "PASS"


# ==================== ROUTES ====================


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Rule #1 Investing API",
        "version": "2.0.0",
        "database": "PostgreSQL",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/api/stocks/{symbol}", response_model=StockData)
async def get_stock_data(symbol: str, db: Session = Depends(get_db), force_refresh: bool = False):
    """
    Fetch comprehensive stock data including growth rates and current metrics.
    Uses database caching to reduce API calls.

    - **symbol**: Stock ticker symbol (e.g., AAPL, MSFT)
    - **force_refresh**: Force refresh from API, bypassing cache
    """
    symbol = symbol.upper()

    # Check cache first (unless force refresh)
    if not force_refresh:
        cached = db.query(StockCache).filter(StockCache.symbol == symbol, StockCache.expires_at > datetime.utcnow()).first()

        if cached:
            return StockData(
                symbol=cached.symbol,
                company_name=cached.company_name or "",
                sector=cached.sector,
                industry=cached.industry,
                description=cached.description,
                current_metrics=CurrentMetrics(
                    price=cached.current_price or 0,
                    eps=cached.eps or 0,
                    pe_ratio=cached.pe_ratio or 0,
                    book_value=cached.book_value or 0,
                    dividend_yield=cached.dividend_yield or 0,
                    roe=cached.roe or 0,
                    profit_margin=cached.profit_margin or 0,
                    market_cap=cached.market_cap or 0,
                ),
                growth_rates=GrowthRates(
                    book_value=cached.book_value_growth or 0,
                    eps=cached.eps_growth or 0,
                    cash_flow=cached.cash_flow_growth or 0,
                    sales=cached.sales_growth or 0,
                    roic=cached.roic or 0,
                ),
                fetched_at=cached.fetched_at,
            )

    try:
        # Fetch data from Alpha Vantage
        overview_task = alpha_vantage.fetch("OVERVIEW", symbol, db)
        quote_task = alpha_vantage.fetch("GLOBAL_QUOTE", symbol, db)
        income_task = alpha_vantage.fetch("INCOME_STATEMENT", symbol, db)
        balance_task = alpha_vantage.fetch("BALANCE_SHEET", symbol, db)
        cashflow_task = alpha_vantage.fetch("CASH_FLOW", symbol, db)

        overview, quote, income, balance, cashflow = await asyncio.gather(
            overview_task, quote_task, income_task, balance_task, cashflow_task
        )

        if not overview.get("Symbol"):
            raise HTTPException(status_code=404, detail=f"Stock symbol {symbol} not found")

        quote_data = quote.get("Global Quote", {})
        income_statements = income.get("annualReports", [])
        balance_sheets = balance.get("annualReports", [])
        cash_flows = cashflow.get("annualReports", [])

        growth_rates = calculate_growth_rates(income_statements, balance_sheets, cash_flows)

        current_metrics = CurrentMetrics(
            price=float(quote_data.get("05. price", 0)),
            eps=float(overview.get("EPS", 0)),
            pe_ratio=float(overview.get("PERatio", 0)),
            book_value=float(overview.get("BookValue", 0)),
            dividend_yield=float(overview.get("DividendYield", 0)),
            roe=float(overview.get("ReturnOnEquityTTM", 0)),
            profit_margin=float(overview.get("ProfitMargin", 0)),
            market_cap=float(overview.get("MarketCapitalization", 0)),
        )

        # Update cache in database
        cached = db.query(StockCache).filter(StockCache.symbol == symbol).first()
        now = datetime.utcnow()

        if cached:
            # Update existing cache
            cached.company_name = overview.get("Name", "")
            cached.sector = overview.get("Sector")
            cached.industry = overview.get("Industry")
            cached.description = overview.get("Description")
            cached.current_price = current_metrics.price
            cached.eps = current_metrics.eps
            cached.pe_ratio = current_metrics.pe_ratio
            cached.book_value = current_metrics.book_value
            cached.dividend_yield = current_metrics.dividend_yield
            cached.roe = current_metrics.roe
            cached.profit_margin = current_metrics.profit_margin
            cached.market_cap = current_metrics.market_cap
            cached.book_value_growth = growth_rates.book_value
            cached.eps_growth = growth_rates.eps
            cached.cash_flow_growth = growth_rates.cash_flow
            cached.sales_growth = growth_rates.sales
            cached.roic = growth_rates.roic
            cached.fetched_at = now
            cached.expires_at = now + timedelta(hours=1)
        else:
            # Create new cache entry
            cached = StockCache(
                symbol=symbol,
                company_name=overview.get("Name", ""),
                sector=overview.get("Sector"),
                industry=overview.get("Industry"),
                description=overview.get("Description"),
                current_price=current_metrics.price,
                eps=current_metrics.eps,
                pe_ratio=current_metrics.pe_ratio,
                book_value=current_metrics.book_value,
                dividend_yield=current_metrics.dividend_yield,
                roe=current_metrics.roe,
                profit_margin=current_metrics.profit_margin,
                market_cap=current_metrics.market_cap,
                book_value_growth=growth_rates.book_value,
                eps_growth=growth_rates.eps,
                cash_flow_growth=growth_rates.cash_flow,
                sales_growth=growth_rates.sales,
                roic=growth_rates.roic,
                fetched_at=now,
                expires_at=now + timedelta(hours=1),
            )
            db.add(cached)

        db.commit()

        return StockData(
            symbol=symbol,
            company_name=overview.get("Name", ""),
            sector=overview.get("Sector"),
            industry=overview.get("Industry"),
            description=overview.get("Description"),
            current_metrics=current_metrics,
            growth_rates=growth_rates,
            fetched_at=now,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing stock data: {str(e)}")


@app.post("/api/valuation", response_model=ValuationOutput)
async def calculate_valuation(valuation: ValuationInput, current_price: float = Query(...)):
    """
    Calculate Sticker Price and Margin of Safety price.

    Uses Phil Town's Rule #1 formula to determine intrinsic value.
    """
    try:
        sticker = calculate_sticker_price(valuation.current_eps, valuation.growth_rate, valuation.pe_ratio)

        mos = sticker * 0.5
        discount = ((current_price / sticker) * 100) if sticker > 0 else 0

        if current_price <= mos:
            recommendation = "BUY - On Sale!"
        elif current_price <= sticker:
            recommendation = "WAIT - Not enough margin"
        else:
            recommendation = "AVOID - Overvalued"

        return ValuationOutput(
            sticker_price=sticker,
            mos_price=mos,
            current_price=current_price,
            recommendation=recommendation,
            discount_percentage=discount,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error calculating valuation: {str(e)}")


@app.get("/api/moat/evaluate", response_model=MoatEvaluation)
async def evaluate_moat(
    book_value: float = Query(..., ge=0, le=100),
    eps: float = Query(..., ge=0, le=100),
    cash_flow: float = Query(..., ge=0, le=100),
    sales: float = Query(..., ge=0, le=100),
    roic: float = Query(..., ge=0, le=100),
):
    """
    Evaluate if a company has a wide moat based on the Big Five growth rates.

    All rates should be 10%+ annually to indicate a durable competitive advantage.
    """
    rates = [book_value, eps, cash_flow, sales, roic]
    avg_rate = sum(rates) / len(rates)
    all_above_10 = all(rate >= 10 for rate in rates)

    return MoatEvaluation(
        has_wide_moat=all_above_10,
        average_growth_rate=round(avg_rate, 2),
        rates=GrowthRates(book_value=book_value, eps=eps, cash_flow=cash_flow, sales=sales, roic=roic),
        passing_metrics=sum(1 for rate in rates if rate >= 10),
        total_metrics=len(rates),
        assessment="PASS - Wide moat" if all_above_10 else "FAIL - Insufficient moat",
    )


@app.post("/api/analyses", response_model=AnalysisResponse)
async def create_analysis(analysis: AnalysisCreate, db: Session = Depends(get_db)):
    """
    Save a stock analysis with user scores for the Four Ms.
    """
    try:
        overall_score = calculate_overall_score(
            analysis.meaning_score, analysis.moat_score, analysis.management_score, analysis.margin_score
        )

        recommendation = get_recommendation(overall_score)

        db_analysis = Analysis(
            symbol=analysis.symbol.upper(),
            company_name=analysis.company_name,
            meaning_score=analysis.meaning_score,
            moat_score=analysis.moat_score,
            management_score=analysis.management_score,
            margin_score=analysis.margin_score,
            overall_score=overall_score,
            recommendation=recommendation,
            user_notes=analysis.user_notes,
            current_price=analysis.current_price,
            sticker_price=analysis.sticker_price,
            mos_price=analysis.mos_price,
            book_value_growth=analysis.book_value_growth,
            eps_growth=analysis.eps_growth,
            cash_flow_growth=analysis.cash_flow_growth,
            sales_growth=analysis.sales_growth,
            roic=analysis.roic,
        )

        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)

        return AnalysisResponse.from_orm(db_analysis)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating analysis: {str(e)}")


@app.get("/api/analyses", response_model=List[AnalysisResponse])
async def list_analyses(
    symbol: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    List saved analyses, optionally filtered by symbol.
    """
    query = db.query(Analysis)

    if symbol:
        query = query.filter(Analysis.symbol == symbol.upper())

    analyses = query.order_by(desc(Analysis.created_at)).offset(skip).limit(limit).all()

    return [AnalysisResponse.from_orm(a) for a in analyses]


@app.get("/api/analyses/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """
    Get a specific analysis by ID.
    """
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return AnalysisResponse.from_orm(analysis)


@app.put("/api/analyses/{analysis_id}", response_model=AnalysisResponse)
async def update_analysis(analysis_id: int, analysis_update: AnalysisUpdate, db: Session = Depends(get_db)):
    """
    Update an existing analysis.
    """
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    # Update fields
    if analysis_update.meaning_score is not None:
        analysis.meaning_score = analysis_update.meaning_score
    if analysis_update.moat_score is not None:
        analysis.moat_score = analysis_update.moat_score
    if analysis_update.management_score is not None:
        analysis.management_score = analysis_update.management_score
    if analysis_update.margin_score is not None:
        analysis.margin_score = analysis_update.margin_score
    if analysis_update.user_notes is not None:
        analysis.user_notes = analysis_update.user_notes

    # Recalculate overall score
    analysis.overall_score = calculate_overall_score(
        analysis.meaning_score, analysis.moat_score, analysis.management_score, analysis.margin_score
    )
    analysis.recommendation = get_recommendation(analysis.overall_score)
    analysis.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(analysis)

    return AnalysisResponse.from_orm(analysis)


@app.delete("/api/analyses/{analysis_id}")
async def delete_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """
    Delete an analysis.
    """
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    db.delete(analysis)
    db.commit()

    return {"message": "Analysis deleted successfully", "id": analysis_id}


@app.get("/api/analyses/stats", response_model=AnalysisStats)
async def get_analysis_stats(db: Session = Depends(get_db)):
    """
    Get statistics about saved analyses.
    """
    total = db.query(func.count(Analysis.id)).scalar()
    avg_score = db.query(func.avg(Analysis.overall_score)).scalar() or 0

    # Count by recommendation
    recommendations = db.query(Analysis.recommendation, func.count(Analysis.id)).group_by(Analysis.recommendation).all()

    recs_dict = {rec: count for rec, count in recommendations}

    # Top analyzed symbols
    top_symbols = (
        db.query(Analysis.symbol, func.count(Analysis.id).label("count"))
        .group_by(Analysis.symbol)
        .order_by(desc("count"))
        .limit(10)
        .all()
    )

    top_list = [{"symbol": sym, "count": count} for sym, count in top_symbols]

    return AnalysisStats(
        total_analyses=total, average_score=round(avg_score, 2), analyses_by_recommendation=recs_dict, top_symbols=top_list
    )


# ==================== WATCHLIST ENDPOINTS ====================


@app.post("/api/watchlist", response_model=WatchlistResponse)
async def create_watchlist_item(item: WatchlistCreate, db: Session = Depends(get_db)):
    """
    Add a stock to the watchlist.
    """
    try:
        db_item = Watchlist(
            user_id=1,  # TODO: Get from auth
            symbol=item.symbol.upper(),
            company_name=item.company_name,
            target_buy_price=item.target_buy_price,
            target_sell_price=item.target_sell_price,
            alert_enabled=item.alert_enabled,
            alert_price=item.alert_price,
            notes=item.notes,
        )

        db.add(db_item)
        db.commit()
        db.refresh(db_item)

        return WatchlistResponse.from_orm(db_item)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating watchlist item: {str(e)}")


@app.get("/api/watchlist", response_model=List[WatchlistResponse])
async def list_watchlist(limit: int = Query(50, ge=1, le=100), skip: int = Query(0, ge=0), db: Session = Depends(get_db)):
    """
    List all watchlist items.
    """
    items = db.query(Watchlist).order_by(desc(Watchlist.created_at)).offset(skip).limit(limit).all()
    return [WatchlistResponse.from_orm(item) for item in items]


@app.get("/api/watchlist/{item_id}", response_model=WatchlistResponse)
async def get_watchlist_item(item_id: int, db: Session = Depends(get_db)):
    """
    Get a specific watchlist item.
    """
    item = db.query(Watchlist).filter(Watchlist.id == item_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Watchlist item not found")

    return WatchlistResponse.from_orm(item)


@app.put("/api/watchlist/{item_id}", response_model=WatchlistResponse)
async def update_watchlist_item(item_id: int, item_update: WatchlistUpdate, db: Session = Depends(get_db)):
    """
    Update a watchlist item.
    """
    item = db.query(Watchlist).filter(Watchlist.id == item_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Watchlist item not found")

    if item_update.target_buy_price is not None:
        item.target_buy_price = item_update.target_buy_price
    if item_update.target_sell_price is not None:
        item.target_sell_price = item_update.target_sell_price
    if item_update.alert_enabled is not None:
        item.alert_enabled = item_update.alert_enabled
    if item_update.alert_price is not None:
        item.alert_price = item_update.alert_price
    if item_update.notes is not None:
        item.notes = item_update.notes

    item.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(item)

    return WatchlistResponse.from_orm(item)


@app.delete("/api/watchlist/{item_id}")
async def delete_watchlist_item(item_id: int, db: Session = Depends(get_db)):
    """
    Delete a watchlist item.
    """
    item = db.query(Watchlist).filter(Watchlist.id == item_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Watchlist item not found")

    db.delete(item)
    db.commit()

    return {"message": "Watchlist item deleted successfully", "id": item_id}


# ==================== RUN SERVER ====================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
