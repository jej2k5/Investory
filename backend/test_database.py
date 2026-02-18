from sqlalchemy import create_engine, text

import database


def test_ensure_watchlist_schema_compatibility_adds_missing_columns(monkeypatch):
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE watchlists (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    symbol VARCHAR(10) NOT NULL,
                    company_name VARCHAR(255),
                    target_buy_price FLOAT,
                    target_sell_price FLOAT,
                    alert_enabled BOOLEAN,
                    alert_price FLOAT,
                    created_at DATETIME,
                    updated_at DATETIME
                )
                """
            )
        )

    monkeypatch.setattr(database, "engine", engine)

    database.ensure_watchlist_schema_compatibility()

    with engine.begin() as conn:
        result = conn.execute(text("PRAGMA table_info(watchlists)"))
        columns = {row[1] for row in result.fetchall()}

    assert "moat_score" in columns
    assert "moat_assessment" in columns
    assert "has_wide_moat" in columns
    assert "book_value_growth" in columns
    assert "eps_growth" in columns
    assert "cash_flow_growth" in columns
    assert "sales_growth" in columns
    assert "roic" in columns
    assert "notes" in columns
