"""
Basic tests for Investory API
"""

from main import (
    _safe_float,
    calculate_cagr,
    calculate_growth_rates,
    calculate_overall_score,
    calculate_sticker_price,
    get_recommendation,
)


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
