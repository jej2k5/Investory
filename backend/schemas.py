"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime

# ==================== USER SCHEMAS ====================

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool

    class Config:
        from_attributes = True

# ==================== ANALYSIS SCHEMAS ====================

class AnalysisBase(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10)
    company_name: Optional[str] = None
    meaning_score: Optional[int] = Field(None, ge=1, le=5)
    moat_score: Optional[int] = Field(None, ge=1, le=5)
    management_score: Optional[int] = Field(None, ge=1, le=5)
    margin_score: Optional[int] = Field(None, ge=1, le=5)
    user_notes: Optional[str] = None
    
    @validator('symbol')
    def symbol_uppercase(cls, v):
        return v.upper() if v else v

class AnalysisCreate(AnalysisBase):
    # Additional fields for creating analysis
    current_price: Optional[float] = None
    sticker_price: Optional[float] = None
    mos_price: Optional[float] = None
    book_value_growth: Optional[float] = None
    eps_growth: Optional[float] = None
    cash_flow_growth: Optional[float] = None
    sales_growth: Optional[float] = None
    roic: Optional[float] = None

class AnalysisUpdate(BaseModel):
    meaning_score: Optional[int] = Field(None, ge=1, le=5)
    moat_score: Optional[int] = Field(None, ge=1, le=5)
    management_score: Optional[int] = Field(None, ge=1, le=5)
    margin_score: Optional[int] = Field(None, ge=1, le=5)
    user_notes: Optional[str] = None

class AnalysisResponse(AnalysisBase):
    id: int
    user_id: Optional[int] = None
    overall_score: Optional[float] = None
    recommendation: Optional[str] = None
    current_price: Optional[float] = None
    sticker_price: Optional[float] = None
    mos_price: Optional[float] = None
    book_value_growth: Optional[float] = None
    eps_growth: Optional[float] = None
    cash_flow_growth: Optional[float] = None
    sales_growth: Optional[float] = None
    roic: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ==================== WATCHLIST SCHEMAS ====================

class WatchlistBase(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10)
    company_name: Optional[str] = None
    target_buy_price: Optional[float] = Field(None, gt=0)
    target_sell_price: Optional[float] = Field(None, gt=0)
    alert_enabled: bool = False
    alert_price: Optional[float] = Field(None, gt=0)
    notes: Optional[str] = None
    
    @validator('symbol')
    def symbol_uppercase(cls, v):
        return v.upper() if v else v

class WatchlistCreate(WatchlistBase):
    pass

class WatchlistUpdate(BaseModel):
    target_buy_price: Optional[float] = Field(None, gt=0)
    target_sell_price: Optional[float] = Field(None, gt=0)
    alert_enabled: Optional[bool] = None
    alert_price: Optional[float] = Field(None, gt=0)
    notes: Optional[str] = None

class WatchlistResponse(WatchlistBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ==================== STOCK DATA SCHEMAS ====================

class GrowthRates(BaseModel):
    book_value: float = Field(default=0, description="10-year CAGR for book value per share")
    eps: float = Field(default=0, description="10-year CAGR for earnings per share")
    cash_flow: float = Field(default=0, description="10-year CAGR for operating cash flow")
    sales: float = Field(default=0, description="10-year CAGR for sales per share")
    roic: float = Field(default=0, description="Return on invested capital")

class CurrentMetrics(BaseModel):
    price: float
    eps: float
    pe_ratio: float
    book_value: float
    dividend_yield: float
    roe: float
    profit_margin: float
    market_cap: float

class StockData(BaseModel):
    symbol: str
    company_name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    current_metrics: CurrentMetrics
    growth_rates: GrowthRates
    fetched_at: datetime

class StockCacheResponse(BaseModel):
    symbol: str
    company_name: Optional[str]
    current_price: Optional[float]
    fetched_at: datetime
    expires_at: datetime
    is_expired: bool

    class Config:
        from_attributes = True

# ==================== VALUATION SCHEMAS ====================

class ValuationInput(BaseModel):
    current_eps: float = Field(..., gt=0)
    growth_rate: float = Field(..., ge=0, le=100)
    pe_ratio: float = Field(..., gt=0)

class ValuationOutput(BaseModel):
    sticker_price: float
    mos_price: float
    current_price: float
    recommendation: str
    discount_percentage: float

# ==================== MOAT EVALUATION SCHEMAS ====================

class MoatEvaluation(BaseModel):
    has_wide_moat: bool
    average_growth_rate: float
    rates: GrowthRates
    passing_metrics: int
    total_metrics: int
    assessment: str

# ==================== STATISTICS SCHEMAS ====================

class AnalysisStats(BaseModel):
    total_analyses: int
    average_score: float
    analyses_by_recommendation: dict
    top_symbols: List[dict]

class UserStats(BaseModel):
    total_users: int
    active_users: int
    total_analyses: int
    total_watchlist_items: int
