import asyncio

from fastapi import HTTPException

from mcp_server import InvestoryMCPService, handle_jsonrpc


def test_mcp_tools_list_exposes_stable_names_and_schemas():
    service = InvestoryMCPService(api_base_url="http://api")
    tools = service.list_tools()

    names = {tool["name"] for tool in tools}
    assert InvestoryMCPService.TOOL_FETCH_STOCK_METRICS in names
    assert InvestoryMCPService.TOOL_CALCULATE_VALUATION in names
    assert InvestoryMCPService.TOOL_EVALUATE_MOAT in names
    assert InvestoryMCPService.TOOL_WATCHLIST_CREATE in names

    watchlist_schema = next(t["inputSchema"] for t in tools if t["name"] == InvestoryMCPService.TOOL_WATCHLIST_CREATE)
    assert "symbol" in watchlist_schema["properties"]


def test_mcp_validation_rejects_invalid_payload_shape():
    service = InvestoryMCPService(api_base_url="http://api")

    response = asyncio.run(
        handle_jsonrpc(
            service,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": InvestoryMCPService.TOOL_WATCHLIST_CREATE,
                    "arguments": {"symbol": "AAPL", "target_buy_price": -1, "auth_token": "token"},
                },
            },
        )
    )

    assert response["error"]["code"] == -32602


def test_mcp_initialize_returns_lifecycle_metadata():
    service = InvestoryMCPService(api_base_url="http://api")

    response = asyncio.run(
        handle_jsonrpc(
            service,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {},
            },
        )
    )

    assert response["result"]["protocolVersion"] == InvestoryMCPService.MCP_PROTOCOL_VERSION
    assert "tools" in response["result"]["capabilities"]
    assert "resources" in response["result"]["capabilities"]
    assert response["result"]["serverInfo"]["name"] == "investory-mcp"


def test_mcp_tolerates_notifications_initialized():
    service = InvestoryMCPService(api_base_url="http://api")

    response = asyncio.run(
        handle_jsonrpc(
            service,
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "notifications/initialized",
                "params": {},
            },
        )
    )

    assert response["result"] == {}


def test_mcp_ping_returns_empty_result():
    service = InvestoryMCPService(api_base_url="http://api")

    response = asyncio.run(
        handle_jsonrpc(
            service,
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "ping",
                "params": {},
            },
        )
    )

    assert response["result"] == {}


def test_watchlist_tools_require_authentication():
    service = InvestoryMCPService(api_base_url="http://api")

    try:
        asyncio.run(service.call_tool(InvestoryMCPService.TOOL_WATCHLIST_LIST, {"limit": 5, "skip": 0}))
    except HTTPException as exc:
        assert exc.status_code == 401
    else:
        raise AssertionError("Expected unauthenticated access to fail")


def test_mcp_tool_routing_for_moat_evaluation(monkeypatch):
    service = InvestoryMCPService(api_base_url="http://api")

    async def fake_api_request(*args, **kwargs):
        return {"has_wide_moat": True}

    monkeypatch.setattr(service, "_api_request", fake_api_request)

    response = asyncio.run(
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


def test_watchlist_delete_returns_404_from_api(monkeypatch):
    service = InvestoryMCPService(api_base_url="http://api")

    async def fake_api_request(method, path, **kwargs):
        raise HTTPException(status_code=404, detail="Watchlist item not found")

    monkeypatch.setattr(service, "_api_request", fake_api_request)

    try:
        asyncio.run(
            service.call_tool(
                InvestoryMCPService.TOOL_WATCHLIST_DELETE,
                {"item_id": 777, "auth_token": "token"},
            )
        )
    except HTTPException as exc:
        assert exc.status_code == 404
    else:
        raise AssertionError("Expected 404 to pass through")
