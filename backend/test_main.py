"""
Basic tests for Investory API
"""

from main import calculate_cagr, calculate_overall_score, calculate_sticker_price, get_recommendation


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
