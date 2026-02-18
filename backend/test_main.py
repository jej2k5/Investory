"""
Basic tests for Investory API
"""

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import get_db
from main import (
    _safe_float,
    app,
    get_current_user,
    calculate_cagr,
    calculate_growth_rates,
    calculate_overall_score,
    calculate_sticker_price,
    get_recommendation,
)
from models import Base, User


def test_calculate_cagr_basic():
    """Test CAGR calculation with known values"""
    result = calculate_cagr(100, 200, 10)
    assert round(result, 2) == 7.18


def test_calculate_cagr_zero_start():
    """CAGR with zero start value should return 0"""
    assert calculate_cagr(0, 200, 10) == 0.0


def test_calculate_cagr_zero_years():
    """CAGR with zero years should return 0"""
    assert calculate_cagr(100, 200, 0) == 0.0


def test_calculate_sticker_price():
    """Test sticker price calculation"""
    result = calculate_sticker_price(5.0, 15.0, 30.0)
    assert result > 0


def test_calculate_sticker_price_zero_eps():
    """Sticker price with zero EPS"""
    result = calculate_sticker_price(0, 15.0, 30.0)
    assert result == 0.0


def test_calculate_overall_score():
    """Test overall score calculation"""
    result = calculate_overall_score(4, 5, 3, 4)
    assert result == 4.0


def test_calculate_overall_score_with_none():
    """Overall score should ignore None values"""
    result = calculate_overall_score(4, None, 3, None)
    assert result == 3.5


def test_calculate_overall_score_all_none():
    """Overall score with all None should return 0"""
    result = calculate_overall_score(None, None, None, None)
    assert result == 0.0


def test_get_recommendation_strong_buy():
    assert get_recommendation(4.5) == "STRONG BUY"


def test_get_recommendation_buy():
    assert get_recommendation(3.5) == "BUY"


def test_get_recommendation_hold():
    assert get_recommendation(3.0) == "HOLD"


def test_get_recommendation_pass():
    assert get_recommendation(2.0) == "PASS"


def test_safe_float_handles_none_strings():
    assert _safe_float("None") == 0.0
    assert _safe_float(None) == 0.0
    assert _safe_float("123.45") == 123.45


def test_growth_rates_survive_none_and_calculate_remaining_metrics():
    income_data = [
        {"totalRevenue": "200", "netIncome": "None"},
        {"totalRevenue": "100", "netIncome": "50"},
    ]
    balance_data = [
        {
            "totalShareholderEquity": "300",
            "longTermDebt": "100",
            "cashAndCashEquivalentsAtCarryingValue": "50",
        },
        {"totalShareholderEquity": "200"},
    ]
    cash_flow_data = [
        {"operatingCashflow": "120"},
        {"operatingCashflow": "100"},
    ]

    result = calculate_growth_rates(income_data, balance_data, cash_flow_data)

    assert round(result.sales, 2) == 100.0
    assert round(result.eps, 2) == -100.0
    assert round(result.book_value, 2) == 50.0
    assert round(result.cash_flow, 2) == 20.0
    assert round(result.roic, 2) == 0.0


def test_growth_rates_uses_nine_year_span_for_ten_reports():
    income_data = [{"totalRevenue": "200"}] + [{"totalRevenue": "0"}] * 8 + [{"totalRevenue": "100"}]

    result = calculate_growth_rates(income_data, [], [])

    assert round(result.sales, 2) == 8.01


def test_watchlist_moat_fields_round_trip_create_list_get_update():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        with TestingSessionLocal() as db:
            user = User(username="testuser", hashed_password="hashed", role="user", is_active=True, requires_password_change=False)
            db.add(user)
            db.commit()
            db.refresh(user)

        def override_current_user():
            with TestingSessionLocal() as db:
                return db.query(User).filter(User.id == user.id).first()

        app.dependency_overrides[get_current_user] = override_current_user

        payload = {
            "symbol": "msft",
            "company_name": "Microsoft",
            "target_buy_price": 250,
            "target_sell_price": 380,
            "alert_enabled": True,
            "moat_score": 5,
            "moat_assessment": "WIDE MOAT",
            "has_wide_moat": True,
            "book_value_growth": 12.2,
            "eps_growth": 14.5,
            "cash_flow_growth": 11.1,
            "sales_growth": 10.8,
            "roic": 18.4,
        }

        create_response = client.post("/api/watchlist", json=payload)
        assert create_response.status_code == 200
        created = create_response.json()
        assert created["symbol"] == "MSFT"
        assert created["moat_score"] == 5
        assert created["moat_assessment"] == "WIDE MOAT"
        assert created["has_wide_moat"] is True
        assert created["book_value_growth"] == 12.2
        assert created["eps_growth"] == 14.5
        assert created["cash_flow_growth"] == 11.1
        assert created["sales_growth"] == 10.8
        assert created["roic"] == 18.4

        list_response = client.get("/api/watchlist")
        assert list_response.status_code == 200
        listed = list_response.json()
        assert len(listed) == 1
        assert listed[0]["moat_score"] == 5
        assert listed[0]["moat_assessment"] == "WIDE MOAT"

        item_id = created["id"]
        get_response = client.get(f"/api/watchlist/{item_id}")
        assert get_response.status_code == 200
        fetched = get_response.json()
        assert fetched["has_wide_moat"] is True
        assert fetched["sales_growth"] == 10.8

        update_response = client.put(
            f"/api/watchlist/{item_id}",
            json={
                "moat_score": 4,
                "moat_assessment": "NARROW MOAT",
                "has_wide_moat": False,
                "sales_growth": 9.2,
                "roic": 15.0,
            },
        )
        assert update_response.status_code == 200
        updated = update_response.json()
        assert updated["moat_score"] == 4
        assert updated["moat_assessment"] == "NARROW MOAT"
        assert updated["has_wide_moat"] is False
        assert updated["sales_growth"] == 9.2
        assert updated["roic"] == 15.0

    app.dependency_overrides.clear()
