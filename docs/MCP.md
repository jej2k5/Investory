# Investory MCP Integration Guide

Investory includes a dedicated MCP service (`backend/mcp_server.py`) that exposes stock analysis and watchlist workflows as MCP tools/resources over JSON-RPC.

## Transports

The service supports:

- **stdio transport** (default): line-delimited JSON-RPC on stdin/stdout.
- **HTTP transport**: `POST /mcp` on port `8090` by default.

### Run locally (stdio)

```bash
cd backend
python mcp_server.py --transport stdio
```

### Run locally (HTTP)

```bash
cd backend
python mcp_server.py --transport http --host 0.0.0.0 --port 8090
```

### Docker Compose

`compose.yml` now includes an `mcp` service. Start it with:

```bash
docker compose up -d mcp
```

Then connect MCP clients to:

- `http://localhost:8090/mcp` (HTTP JSON-RPC transport)

Compose config now uses `INVESTORY_API_BASE_URL` for MCP service API targeting (default: `http://backend:8000`) instead of DB connection variables.

The MCP service proxies to the backend API and does not connect to the database directly.

## Connector compatibility

The MCP JSON-RPC router supports connector lifecycle methods used by common MCP clients:

- `initialize` returns protocol metadata with `protocolVersion: "2024-11-05"`, declared `tools`/`resources` capabilities, and `serverInfo` for Investory MCP.
- `notifications/initialized` is tolerated as a no-op success path.
- `ping` is supported and returns an empty success result (`{}`).

## Architecture note: API layer vs direct DB

The MCP server should use the same API/domain layer functions as REST endpoints for business operations (especially watchlist ownership checks), instead of duplicating DB CRUD logic in MCP handlers. This keeps behavior consistent across REST and MCP and reduces permission drift risk.

## Authentication strategy

Watchlist tools/resources enforce user ownership and require an authenticated user. The MCP service supports two auth modes:

1. **Token passthrough** (recommended)
   - Pass the API bearer token as `auth_token` in MCP tool arguments/resource params.
2. **Service token fallback**
   - Configure `MCP_SERVICE_AUTH_TOKEN` in environment.
   - If no token is provided per call, MCP uses this bearer token for watchlist calls.

> Note: stock metrics, valuation, and moat evaluation tools are read-only and do not require auth.

## Stable tool names

- `investory.fetch_stock_metrics`
- `investory.calculate_valuation`
- `investory.evaluate_moat`
- `investory.watchlist.list`
- `investory.watchlist.create`
- `investory.watchlist.update`
- `investory.watchlist.delete`

Schemas are generated from existing FastAPI/Pydantic contracts (`backend/schemas.py`) using `model_json_schema()` to keep MCP and REST validation aligned.

## Resources

- `investory://schemas/tools` – returns JSON schema metadata for all tools.
- `investory://watchlist` – authenticated watchlist view for current user.

## Sample JSON-RPC calls

### 1) List tools

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list"
}
```

### 2) Fetch stock metrics

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "investory.fetch_stock_metrics",
    "arguments": {
      "symbol": "AAPL"
    }
  }
}
```

### 3) Calculate valuation

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "investory.calculate_valuation",
    "arguments": {
      "current_eps": 6.15,
      "growth_rate": 14.2,
      "pe_ratio": 28.5,
      "current_price": 175.5
    }
  }
}
```

### 4) Create watchlist item (token passthrough)

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/call",
  "params": {
    "name": "investory.watchlist.create",
    "arguments": {
      "auth_token": "<JWT_ACCESS_TOKEN>",
      "symbol": "MSFT",
      "company_name": "Microsoft",
      "target_buy_price": 300
    }
  }
}
```

### 5) Read watchlist resource

```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "resources/read",
  "params": {
    "uri": "investory://watchlist",
    "params": {
      "auth_token": "<JWT_ACCESS_TOKEN>"
    }
  }
}
```

## Example MCP client config (HTTP)

```json
{
  "mcpServers": {
    "investory": {
      "transport": {
        "type": "http",
        "url": "http://localhost:8090/mcp"
      }
    }
  }
}
```
