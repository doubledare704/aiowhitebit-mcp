# aiowhitebit-mcp

Message Control Protocol (MCP) server and client implementation for WhiteBit cryptocurrency exchange API. Built on top of [aiowhitebit](https://github.com/doubledare704/aiowhitebit) library and [fastmcp](https://github.com/jlowin/fastmcp).

## Features

- MCP server for WhiteBit API with public and private endpoints
- Support for WebSocket API
- Easy-to-use client for interacting with the MCP server
- Command-line interface for running the server
- Support for multiple transport protocols (stdio, SSE, WebSocket)
- Integration with Claude Desktop

## Installation

```bash
pip install aiowhitebit-mcp
```

Or install from source:

```bash
git clone https://github.com/yourusername/aiowhitebit-mcp.git
cd aiowhitebit-mcp
pip install -e .
```

## Usage

### Running the MCP Server

You can run the MCP server using the command-line interface:

```bash
# Run with stdio transport (for Claude Desktop)
aiowhitebit-mcp --transport stdio

# Run with SSE transport (for web clients)
aiowhitebit-mcp --transport sse --host 127.0.0.1 --port 8000

# Run with WebSocket transport
aiowhitebit-mcp --transport ws --host 127.0.0.1 --port 8000
```

For private API endpoints, you need to provide your WhiteBit API credentials:

```bash
# Using environment variables
export WHITEBIT_API_KEY="your_api_key"
export WHITEBIT_API_SECRET="your_api_secret"
aiowhitebit-mcp

# Or using command-line arguments
aiowhitebit-mcp --api-key "your_api_key" --api-secret "your_api_secret"
```

### Using the MCP Server with Claude Desktop

1. Install the MCP server in Claude Desktop:

```bash
fastmcp install examples/run_server.py --name "WhiteBit API"
```

2. Open Claude Desktop and select the "WhiteBit API" MCP server from the list of available servers.

3. You can now interact with the WhiteBit API through Claude.

### Using the Client

```python
import asyncio
from aiowhitebit_mcp.client import WhiteBitMCPClient

async def main():
    # Connect to the MCP server
    async with WhiteBitMCPClient(server_url="http://localhost:8000/mcp") as client:
        # Get server time
        server_time = await client.get_server_time()
        print("Server time:", server_time)

        # Get market info for BTC_USDT
        btc_usdt_info = await client.get_market_resource("BTC_USDT")
        print("BTC_USDT market info:", btc_usdt_info)

        # Get recent trades for BTC_USDT
        recent_trades = await client.get_recent_trades("BTC_USDT", limit=5)
        print("Recent BTC_USDT trades:", recent_trades)

if __name__ == "__main__":
    asyncio.run(main())
```

## Available Tools and Resources

### Public API Tools

- `get_market_info`: Get information about all available markets
- `get_market_activity`: Get activity information for all markets
- `get_server_time`: Get current server time
- `get_server_status`: Get current server status
- `get_asset_status_list`: Get status of all assets
- `get_orderbook`: Get orderbook for a specific market
- `get_recent_trades`: Get recent trades for a specific market
- `get_fee`: Get trading fee for a specific market

### Private API Tools (requires API credentials)

- `get_trading_balance`: Get trading balance for all assets
- `create_limit_order`: Create a limit order
- `create_stop_limit_order`: Create a stop limit order
- `active_orders`: Get active orders
- `cancel_order`: Cancel an order

### WebSocket Tools

- `get_last_price`: Get last price for a specific market using WebSocket
- `get_market_depth`: Get market depth for a specific market using WebSocket

### Resources

- `whitebit://markets`: Get information about all available markets
- `whitebit://markets/{market}`: Get information about a specific market
- `whitebit://assets`: Get status of all assets
- `whitebit://assets/{asset}`: Get status of a specific asset

## Development

### Setup Development Environment

To set up a development environment, clone the repository and install the development dependencies:

```bash
git clone https://github.com/yourusername/aiowhitebit-mcp.git
cd aiowhitebit-mcp

# Option 1: Using requirements-dev.txt
pip install -r requirements-dev.txt
pip install -e .

# Option 2: Using pip extras
pip install -e ".[dev]"
```

### Running Tests

To run the tests:

```bash
python -m pytest
```

To run tests with coverage:

```bash
python -m pytest --cov=aiowhitebit_mcp
```

### Code Formatting

This project uses Black for code formatting and isort for import sorting:

```bash
# Format code
black .

# Sort imports
isort .

# Run linting
flake8 .
```

### Type Checking

To run type checking with mypy:

```bash
mypy src/aiowhitebit_mcp
```

### Pre-commit Hooks

You can install pre-commit hooks to automatically format and check your code before committing:

```bash
pre-commit install
```

## License

Apache License 2.0
