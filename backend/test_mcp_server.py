from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from auth import create_access_token
from mcp_server import InvestoryMCPService, handle_jsonrpc
from models import Base, User, Watchlist


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def _seed_users_and_data():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    user_a = User(username="usera", hashed_password="hashed", role="user", is_active=True, requires_password_change=False)
    user_b = User(username="userb", hashed_password="hashed", role="user", is_active=True, requires_password_change=False)
    db.add_all([user_a, user_b])
    db.commit()
    db.refresh(user_a)
    db.refresh(user_b)

    item_a = Watchlist(user_id=user_a.id, symbol="AAPL", company_name="Apple")
    item_b = Watchlist(user_id=user_b.id, symbol="MSFT", company_name="Microsoft")
    db.add_all([item_a, item_b])
    db.commit()
    db.close()


def _token(username: str) -> str:
    return create_access_token({"sub": username})


def test_mcp_tools_list_exposes_stable_names_and_schemas():
    service = InvestoryMCPService(db_session_factory=TestingSessionLocal)
    tools = service.list_tools()

    names = {tool["name"] for tool in tools}
    assert InvestoryMCPService.TOOL_FETCH_STOCK_METRICS in names
    assert InvestoryMCPService.TOOL_CALCULATE_VALUATION in names
    assert InvestoryMCPService.TOOL_EVALUATE_MOAT in names
    assert InvestoryMCPService.TOOL_WATCHLIST_CREATE in names

    watchlist_schema = next(t["inputSchema"] for t in tools if t["name"] == InvestoryMCPService.TOOL_WATCHLIST_CREATE)
    assert "symbol" in watchlist_schema["properties"]


def test_mcp_validation_rejects_invalid_payload_shape():
    service = InvestoryMCPService(db_session_factory=TestingSessionLocal)

    response = __import__("asyncio").run(
        handle_jsonrpc(
            service,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": InvestoryMCPService.TOOL_WATCHLIST_CREATE,
                    "arguments": {"symbol": "AAPL", "target_buy_price": -1, "auth_token": _token("usera")},
                },
            },
        )
    )

    assert response["error"]["code"] == -32602


def test_watchlist_tools_are_scoped_to_authenticated_user():
    _seed_users_and_data()
    service = InvestoryMCPService(db_session_factory=TestingSessionLocal)

    listed = __import__("asyncio").run(
        service.call_tool(
            InvestoryMCPService.TOOL_WATCHLIST_LIST,
            {"limit": 50, "skip": 0, "auth_token": _token("usera")},
        )
    )
    assert len(listed["items"]) == 1
    assert listed["items"][0]["symbol"] == "AAPL"

    try:
        __import__("asyncio").run(
            service.call_tool(
                InvestoryMCPService.TOOL_WATCHLIST_DELETE,
                {"item_id": listed["items"][0]["id"] + 1, "auth_token": _token("usera")},
            )
        )
    except HTTPException as exc:
        assert exc.status_code == 404
    else:
        raise AssertionError("Expected a 404 when deleting another user's item")


def test_watchlist_tools_require_authentication():
    _seed_users_and_data()
    service = InvestoryMCPService(db_session_factory=TestingSessionLocal)

    try:
        __import__("asyncio").run(service.call_tool(InvestoryMCPService.TOOL_WATCHLIST_LIST, {"limit": 5, "skip": 0}))
    except HTTPException as exc:
        assert exc.status_code == 401
    else:
        raise AssertionError("Expected unauthenticated access to fail")


def test_mcp_tool_routing_for_moat_evaluation():
    service = InvestoryMCPService(db_session_factory=TestingSessionLocal)

    response = __import__("asyncio").run(
        handle_jsonrpc(
            service,
            {
                "jsonrpc": "2.0",
                "id": 99,
                "method": "tools/call",
                "params": {
                    "name": InvestoryMCPService.TOOL_EVALUATE_MOAT,
                    "arguments": {
                        "book_value": 12,
                        "eps": 13,
                        "cash_flow": 15,
                        "sales": 11,
                        "roic": 14,
                    },
                },
            },
        )
    )

    assert response["result"]["content"][0]["json"]["has_wide_moat"] is True
