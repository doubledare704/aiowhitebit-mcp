# aiowhitebit-mcp

Message Control Protocol (MCP) server and client implementation for WhiteBit cryptocurrency exchange API. Built on top of [aiowhitebit](https://github.com/doubledare704/aiowhitebit) library and [fastmcp](https://github.com/jlowin/fastmcp).

## Features

- MCP server for WhiteBit API with public endpoints
- Support for multiple transport protocols (stdio, SSE, WebSocket)
- Easy-to-use client for interacting with the MCP server
- Command-line interface for running the server
- Integration with Claude Desktop
- Real-time market data via WebSocket
- Comprehensive test coverage and type checking
- Modern development tools (ruff, pyright, pre-commit)

## Quick Start

```bash
# Install the package
pip install aiowhitebit-mcp

# Run the server (stdio transport for Claude Desktop)
aiowhitebit-mcp --transport stdio

# Or run with WebSocket transport
aiowhitebit-mcp --transport ws --host 127.0.0.1 --port 8000
```

## Basic Usage

```python
import asyncio
from aiowhitebit_mcp.client import WhiteBitMCPClient

async def main():
    async with WhiteBitMCPClient() as client:
        # Get market info
        btc_usdt = await client.get_market_resource("BTC_USDT")
        print("BTC/USDT Market Info:", btc_usdt)

        # Get real-time price via WebSocket
        price = await client.get_last_price("BTC_USDT")
        print("Current BTC/USDT price:", price)

        # Get order book
        orderbook = await client.get_orderbook("BTC_USDT")
        print("Order book:", orderbook)

if __name__ == "__main__":
    asyncio.run(main())
```

## Server Configuration

```python
from aiowhitebit_mcp.server import create_server

server = create_server(
    name="WhiteBit API"
)
```

## Available Tools

### Public API
- `get_server_time()`: Get current server time
- `get_market_info()`: Get all markets information
- `get_orderbook(market: str)`: Get order book
- `get_recent_trades(market: str, limit: int = 100)`: Get recent trades
- `get_ticker(market: str)`: Get ticker information
- `get_fee(market: str)`: Get trading fees

### WebSocket API
- `get_last_price(market: str)`: Get real-time price
- `get_market_depth(market: str)`: Get real-time order book

## Development

```bash
# Clone the repository
git clone https://github.com/yourusername/aiowhitebit-mcp.git
cd aiowhitebit-mcp

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run type checking
pyright src/aiowhitebit_mcp

# Run linting
ruff check .
```

## License

Apache License 2.0
