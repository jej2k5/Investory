"""
Database models for Rule #1 Investing Platform
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    """User accounts"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    analyses = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")
    watchlists = relationship("Watchlist", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"


class Analysis(Base):
    """Stock analysis with Four Ms scores"""
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    symbol = Column(String(10), nullable=False, index=True)
    company_name = Column(String(255))
    
    # Four Ms Scores (1-5)
    meaning_score = Column(Integer, CheckConstraint('meaning_score >= 1 AND meaning_score <= 5'))
    moat_score = Column(Integer, CheckConstraint('moat_score >= 1 AND moat_score <= 5'))
    management_score = Column(Integer, CheckConstraint('management_score >= 1 AND management_score <= 5'))
    margin_score = Column(Integer, CheckConstraint('margin_score >= 1 AND margin_score <= 5'))
    
    # Calculated fields
    overall_score = Column(Float)
    recommendation = Column(String(50))
    
    # User notes
    user_notes = Column(Text)
    
    # Financial data snapshot (at time of analysis)
    current_price = Column(Float)
    sticker_price = Column(Float)
    mos_price = Column(Float)
    
    # Growth rates snapshot
    book_value_growth = Column(Float)
    eps_growth = Column(Float)
    cash_flow_growth = Column(Float)
    sales_growth = Column(Float)
    roic = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="analyses")
    
    def __repr__(self):
        return f"<Analysis(id={self.id}, symbol='{self.symbol}', overall_score={self.overall_score})>"


class Watchlist(Base):
    """User watchlist for tracking stocks"""
    __tablename__ = "watchlists"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    symbol = Column(String(10), nullable=False, index=True)
    company_name = Column(String(255))
    
    # Target prices
    target_buy_price = Column(Float)
    target_sell_price = Column(Float)
    
    # Alert settings
    alert_enabled = Column(Boolean, default=False)
    alert_price = Column(Float)
    
    # Notes
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="watchlists")
    
    def __repr__(self):
        return f"<Watchlist(id={self.id}, symbol='{self.symbol}', user_id={self.user_id})>"


class StockCache(Base):
    """Cache for stock data to reduce API calls"""
    __tablename__ = "stock_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), nullable=False, unique=True, index=True)
    
    # Company info
    company_name = Column(String(255))
    sector = Column(String(100))
    industry = Column(String(100))
    description = Column(Text)
    
    # Current metrics
    current_price = Column(Float)
    eps = Column(Float)
    pe_ratio = Column(Float)
    book_value = Column(Float)
    dividend_yield = Column(Float)
    roe = Column(Float)
    profit_margin = Column(Float)
    market_cap = Column(Float)
    
    # Growth rates
    book_value_growth = Column(Float)
    eps_growth = Column(Float)
    cash_flow_growth = Column(Float)
    sales_growth = Column(Float)
    roic = Column(Float)
    
    # Cache metadata
    fetched_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<StockCache(symbol='{self.symbol}', fetched_at={self.fetched_at})>"


class ApiUsage(Base):
    """Track API usage for rate limiting and analytics"""
    __tablename__ = "api_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    endpoint = Column(String(255), nullable=False, index=True)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer)
    response_time_ms = Column(Integer)
    ip_address = Column(String(50))
    user_agent = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<ApiUsage(endpoint='{self.endpoint}', status={self.status_code})>"
