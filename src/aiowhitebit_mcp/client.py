"""Client for interacting with the WhiteBit MCP server."""

import os

from fastmcp.client import Client


class WhiteBitMCPClient:
    """Client for interacting with the WhiteBit MCP server."""

    def __init__(self, server_url: str | None = None):
        """Initialize the WhiteBit MCP client.

        Args:
            server_url: URL of the MCP server. If not provided, will try to use the
                        WHITEBIT_MCP_URL environment variable.
        """
        self.server_url = server_url or os.environ.get("WHITEBIT_MCP_URL")
        if not self.server_url:
            raise ValueError(
                "Server URL must be provided either as an argument or via the WHITEBIT_MCP_URL environment variable"
            )

        self.client = Client(self.server_url)

    async def __aenter__(self):
        """Async context manager entry."""
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.__aexit__(exc_type, exc_val, exc_tb)

    async def get_market_info(self) -> str:
        """Get information about all available markets."""
        result = await self.client.call_tool("get_market_info", {})
        return result[0].text

    async def get_market_activity(self) -> str:
        """Get activity information for all markets (last price, volume, etc.)."""
        result = await self.client.call_tool("get_market_activity", {})
        return result[0].text

    async def get_server_time(self) -> str:
        """Get current server time."""
        result = await self.client.call_tool("get_server_time", {})
        return result[0].text

    async def get_server_status(self) -> str:
        """Get current server status."""
        result = await self.client.call_tool("get_server_status", {})
        return result[0].text

    async def get_asset_status_list(self) -> str:
        """Get status of all assets."""
        result = await self.client.call_tool("get_asset_status_list", {})
        return result[0].text

    async def get_orderbook(self, market: str, limit: int = 100, level: int = 0) -> str:
        """Get orderbook for a specific market.

        Args:
            market: Market pair (e.g., 'BTC_USDT')
            limit: Number of orders to return (default: 100)
            level: Aggregation level (default: 0)
        """
        result = await self.client.call_tool(
            "get_orderbook", {"market": {"market": market}, "limit": limit, "level": level}
        )
        return result[0].text

    async def get_recent_trades(self, market: str, limit: int = 100) -> str:
        """Get recent trades for a specific market.

        Args:
            market: Market pair (e.g., 'BTC_USDT')
            limit: Number of trades to return (default: 100)
        """
        result = await self.client.call_tool("get_recent_trades", {"market": {"market": market}, "limit": limit})
        return result[0].text

    async def get_fee(self, market: str) -> str:
        """Get trading fee for a specific market.

        Args:
            market: Market pair (e.g., 'BTC_USDT')
        """
        result = await self.client.call_tool("get_fee", {"market": {"market": market}})
        return result[0].text

    async def get_last_price(self, market: str) -> dict:
        """Get last price for a specific market using WebSocket.

        Args:
            market: Market pair (e.g., 'BTC_USDT')
        """
        result = await self.client.call_tool("get_last_price", {"market": {"market": market}})
        return result.content[0].text

    async def get_market_depth(self, market: str) -> dict:
        """Get market depth for a specific market using WebSocket.

        Args:
            market: Market pair (e.g., 'BTC_USDT')
        """
        result = await self.client.call_tool("get_market_depth", {"market": {"market": market}})
        return result.content[0].text

    async def get_markets_resource(self) -> str:
        """Get information about all available markets as a resource."""
        result = await self.client.read_resource("whitebit://markets")
        return result[0].text

    async def get_market_resource(self, market: str) -> str:
        """Get information about a specific market as a resource."""
        result = await self.client.read_resource(f"whitebit://markets/{market}")
        return result[0].text

    async def get_assets_resource(self) -> str:
        """Get status of all assets as a resource."""
        result = await self.client.read_resource("whitebit://assets")
        return result[0].text

    async def get_asset_resource(self, asset: str) -> str:
        """Get status of a specific asset as a resource."""
        result = await self.client.read_resource(f"whitebit://assets/{asset}")
        return result[0].text
