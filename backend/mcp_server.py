"""Investory MCP service.

This module exposes a lightweight MCP-compatible interface over:
- stdio (JSON-RPC line-delimited messages)
- HTTP POST /mcp (JSON-RPC request/response)

It reuses existing Pydantic schemas and business logic from the FastAPI API to keep
contracts aligned and avoid duplicate validation rules.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy.orm import Session, sessionmaker

from auth import decode_access_token
from database import SessionLocal
from main import (
    calculate_valuation,
    create_watchlist_item,
    delete_watchlist_item,
    evaluate_moat,
    get_stock_data,
    list_watchlist,
    update_watchlist_item,
)
from models import User
from schemas import ValuationInput, WatchlistCreate, WatchlistUpdate


class StockMetricsInput(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10)


class MoatEvaluationInput(BaseModel):
    book_value: float = Field(..., ge=0, le=100)
    eps: float = Field(..., ge=0, le=100)
    cash_flow: float = Field(..., ge=0, le=100)
    sales: float = Field(..., ge=0, le=100)
    roic: float = Field(..., ge=0, le=100)


class WatchlistListInput(BaseModel):
    limit: int = Field(default=50, ge=1, le=100)
    skip: int = Field(default=0, ge=0)


class WatchlistDeleteInput(BaseModel):
    item_id: int = Field(..., ge=1)


class WatchlistUpdateInput(BaseModel):
    item_id: int = Field(..., ge=1)
    payload: WatchlistUpdate


class ToolEnvelope(BaseModel):
    model_config = ConfigDict(extra="allow")

    auth_token: Optional[str] = None


class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[str | int] = None
    method: str
    params: Dict[str, Any] = Field(default_factory=dict)


@dataclass(frozen=True)
class MCPTool:
    name: str
    description: str
    input_model: type[BaseModel]


class InvestoryMCPService:
    """Core MCP handlers for stock workflows and user-scoped watchlist actions."""

    TOOL_FETCH_STOCK_METRICS = "investory.fetch_stock_metrics"
    TOOL_CALCULATE_VALUATION = "investory.calculate_valuation"
    TOOL_EVALUATE_MOAT = "investory.evaluate_moat"
    TOOL_WATCHLIST_LIST = "investory.watchlist.list"
    TOOL_WATCHLIST_CREATE = "investory.watchlist.create"
    TOOL_WATCHLIST_UPDATE = "investory.watchlist.update"
    TOOL_WATCHLIST_DELETE = "investory.watchlist.delete"

    def __init__(self, db_session_factory: sessionmaker = SessionLocal):
        self.db_session_factory = db_session_factory
        self.tools = {
            self.TOOL_FETCH_STOCK_METRICS: MCPTool(
                name=self.TOOL_FETCH_STOCK_METRICS,
                description="Fetch stock metrics and growth rates for a ticker symbol.",
                input_model=StockMetricsInput,
            ),
            self.TOOL_CALCULATE_VALUATION: MCPTool(
                name=self.TOOL_CALCULATE_VALUATION,
                description="Calculate sticker and margin-of-safety valuation.",
                input_model=ValuationInput,
            ),
            self.TOOL_EVALUATE_MOAT: MCPTool(
                name=self.TOOL_EVALUATE_MOAT,
                description="Evaluate Big Five growth rates for moat strength.",
                input_model=MoatEvaluationInput,
            ),
            self.TOOL_WATCHLIST_LIST: MCPTool(
                name=self.TOOL_WATCHLIST_LIST,
                description="List watchlist items for the authenticated user.",
                input_model=WatchlistListInput,
            ),
            self.TOOL_WATCHLIST_CREATE: MCPTool(
                name=self.TOOL_WATCHLIST_CREATE,
                description="Create a watchlist item for the authenticated user.",
                input_model=WatchlistCreate,
            ),
            self.TOOL_WATCHLIST_UPDATE: MCPTool(
                name=self.TOOL_WATCHLIST_UPDATE,
                description="Update a watchlist item owned by the authenticated user.",
                input_model=WatchlistUpdateInput,
            ),
            self.TOOL_WATCHLIST_DELETE: MCPTool(
                name=self.TOOL_WATCHLIST_DELETE,
                description="Delete a watchlist item owned by the authenticated user.",
                input_model=WatchlistDeleteInput,
            ),
        }

    def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_model.model_json_schema(),
            }
            for tool in self.tools.values()
        ]

    def list_resources(self) -> List[Dict[str, str]]:
        return [
            {
                "uri": "investory://schemas/tools",
                "name": "Tool Schemas",
                "description": "JSON schemas for all MCP tools.",
            },
            {
                "uri": "investory://watchlist",
                "name": "User Watchlist",
                "description": "Authenticated user's watchlist data.",
            },
        ]

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if name not in self.tools:
            raise HTTPException(status_code=404, detail=f"Unknown tool: {name}")

        envelope = ToolEnvelope.model_validate(arguments)
        auth_token = envelope.auth_token
        tool = self.tools[name]

        filtered_args = dict(arguments)
        filtered_args.pop("auth_token", None)
        payload = tool.input_model.model_validate(filtered_args)

        with self.db_session_factory() as db:
            current_user = self._resolve_user(db, auth_token)

            if name == self.TOOL_FETCH_STOCK_METRICS:
                result = await get_stock_data(payload.symbol, db)  # type: ignore[arg-type]
                return result.model_dump(mode="json")

            if name == self.TOOL_CALCULATE_VALUATION:
                if "current_price" not in arguments:
                    raise HTTPException(status_code=422, detail="current_price is required")
                current_price = float(arguments["current_price"])
                result = await calculate_valuation(payload, current_price=current_price)
                return result.model_dump(mode="json")

            if name == self.TOOL_EVALUATE_MOAT:
                result = await evaluate_moat(**payload.model_dump())
                return result.model_dump(mode="json")

            if current_user is None:
                raise HTTPException(status_code=401, detail="Authentication required for watchlist tools")

            if name == self.TOOL_WATCHLIST_LIST:
                items = await list_watchlist(
                    limit=payload.limit,
                    skip=payload.skip,
                    current_user=current_user,
                    db=db,
                )
                return {"items": [item.model_dump(mode="json") for item in items]}

            if name == self.TOOL_WATCHLIST_CREATE:
                created = await create_watchlist_item(payload, current_user=current_user, db=db)
                return created.model_dump(mode="json")

            if name == self.TOOL_WATCHLIST_UPDATE:
                updated = await update_watchlist_item(
                    payload.item_id,
                    payload.payload,
                    current_user=current_user,
                    db=db,
                )
                return updated.model_dump(mode="json")

            deleted = await delete_watchlist_item(payload.item_id, current_user=current_user, db=db)
            return dict(deleted)

    async def read_resource(self, uri: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if uri == "investory://schemas/tools":
            return {"tools": self.list_tools()}

        if uri == "investory://watchlist":
            args = ToolEnvelope.model_validate(params)
            with self.db_session_factory() as db:
                current_user = self._resolve_user(db, args.auth_token)
                if current_user is None:
                    raise HTTPException(status_code=401, detail="Authentication required")

                items = await list_watchlist(limit=100, skip=0, current_user=current_user, db=db)
                return {"items": [item.model_dump(mode="json") for item in items]}

        raise HTTPException(status_code=404, detail=f"Unknown resource URI: {uri}")

    def _resolve_user(self, db: Session, auth_token: Optional[str]) -> Optional[User]:
        if auth_token:
            payload = decode_access_token(auth_token)
            username = payload.get("sub")
            if username:
                user = db.query(User).filter(User.username == username).first()
                if user and user.is_active:
                    return user

        service_account_username = os.getenv("MCP_SERVICE_ACCOUNT_USERNAME")
        if service_account_username:
            return db.query(User).filter(User.username == service_account_username, User.is_active.is_(True)).first()

        return None


def _jsonrpc_result(request: MCPRequest, result: Any) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request.id, "result": result}


def _jsonrpc_error(request: MCPRequest, code: int, message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    error: Dict[str, Any] = {"code": code, "message": message}
    if data:
        error["data"] = data
    return {"jsonrpc": "2.0", "id": request.id, "error": error}


async def handle_jsonrpc(service: InvestoryMCPService, payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        request = MCPRequest.model_validate(payload)
    except ValidationError as exc:
        return {"jsonrpc": "2.0", "id": payload.get("id") if isinstance(payload, dict) else None, "error": {"code": -32600, "message": "Invalid Request", "data": exc.errors()}}

    try:
        if request.method == "tools/list":
            return _jsonrpc_result(request, {"tools": service.list_tools()})

        if request.method == "tools/call":
            name = request.params.get("name")
            arguments = request.params.get("arguments", {})
            if not name:
                return _jsonrpc_error(request, -32602, "Missing tool name")
            result = await service.call_tool(str(name), dict(arguments))
            return _jsonrpc_result(request, {"content": [{"type": "json", "json": result}]})

        if request.method == "resources/list":
            return _jsonrpc_result(request, {"resources": service.list_resources()})

        if request.method == "resources/read":
            uri = request.params.get("uri")
            params = request.params.get("params", {})
            if not uri:
                return _jsonrpc_error(request, -32602, "Missing resource URI")
            result = await service.read_resource(str(uri), dict(params))
            return _jsonrpc_result(request, {"contents": [{"uri": uri, "mimeType": "application/json", "text": json.dumps(result)}]})

        return _jsonrpc_error(request, -32601, f"Method not found: {request.method}")
    except ValidationError as exc:
        return _jsonrpc_error(request, -32602, "Schema validation failed", {"errors": exc.errors()})
    except HTTPException as exc:
        return _jsonrpc_error(request, exc.status_code, str(exc.detail))
    except Exception as exc:  # defensive fallback
        return _jsonrpc_error(request, -32000, f"Internal MCP server error: {exc}")


def create_http_app(service: Optional[InvestoryMCPService] = None) -> FastAPI:
    app = FastAPI(title="Investory MCP", version="1.0.0")
    mcp = service or InvestoryMCPService()

    @app.get("/health")
    async def health() -> Dict[str, str]:
        return {"status": "ok"}

    @app.post("/mcp")
    async def mcp_endpoint(request: Dict[str, Any]) -> Dict[str, Any]:
        return await handle_jsonrpc(mcp, request)

    return app


async def run_stdio_server(service: Optional[InvestoryMCPService] = None) -> None:
    mcp = service or InvestoryMCPService()
    while True:
        line = await asyncio.to_thread(input)
        if not line:
            continue
        payload = json.loads(line)
        response = await handle_jsonrpc(mcp, payload)
        print(json.dumps(response), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Investory MCP service")
    parser.add_argument("--transport", choices=["stdio", "http"], default=os.getenv("MCP_TRANSPORT", "stdio"))
    parser.add_argument("--host", default=os.getenv("MCP_HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.getenv("MCP_PORT", "8090")))
    args = parser.parse_args()

    if args.transport == "stdio":
        asyncio.run(run_stdio_server())
        return

    uvicorn.run(create_http_app(), host=args.host, port=args.port)


if __name__ == "__main__":
    main()
