"""Client for interacting with the WhiteBit MCP server.
"""

import os
from typing import Dict, Optional

from fastmcp import Client


class WhiteBitMCPClient:
    """Client for interacting with the WhiteBit MCP server"""

    def __init__(self, server_url: str = None):
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
        """Async context manager entry"""
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.client.__aexit__(exc_type, exc_val, exc_tb)

    async def get_market_info(self) -> Dict:
        """Get information about all available markets"""
        result = await self.client.call_tool("get_market_info", {})
        return result.content[0].text

    async def get_market_activity(self) -> Dict:
        """Get activity information for all markets (last price, volume, etc.)"""
        result = await self.client.call_tool("get_market_activity", {})
        return result.content[0].text

    async def get_server_time(self) -> Dict:
        """Get current server time"""
        result = await self.client.call_tool("get_server_time", {})
        return result.content[0].text

    async def get_server_status(self) -> Dict:
        """Get current server status"""
        result = await self.client.call_tool("get_server_status", {})
        return result.content[0].text

    async def get_asset_status_list(self) -> Dict:
        """Get status of all assets"""
        result = await self.client.call_tool("get_asset_status_list", {})
        return result.content[0].text

    async def get_orderbook(self, market: str, limit: int = 100, level: int = 0) -> Dict:
        """Get orderbook for a specific market
        
        Args:
            market: Market pair (e.g., 'BTC_USDT')
            limit: Number of orders to return (default: 100)
            level: Aggregation level (default: 0)
        """
        result = await self.client.call_tool(
            "get_orderbook",
            {
                "market": {"market": market},
                "limit": limit,
                "level": level
            }
        )
        return result.content[0].text

    async def get_recent_trades(self, market: str, limit: int = 100) -> Dict:
        """Get recent trades for a specific market
        
        Args:
            market: Market pair (e.g., 'BTC_USDT')
            limit: Number of trades to return (default: 100)
        """
        result = await self.client.call_tool(
            "get_recent_trades",
            {
                "market": {"market": market},
                "limit": limit
            }
        )
        return result.content[0].text

    async def get_fee(self, market: str) -> Dict:
        """Get trading fee for a specific market
        
        Args:
            market: Market pair (e.g., 'BTC_USDT')
        """
        result = await self.client.call_tool(
            "get_fee",
            {
                "market": {"market": market}
            }
        )
        return result.content[0].text

    async def get_trading_balance(self) -> Dict:
        """Get trading balance for all assets"""
        result = await self.client.call_tool("get_trading_balance", {})
        return result.content[0].text

    async def create_limit_order(
        self, market: str, side: str, amount: float, price: float
    ) -> Dict:
        """Create a limit order
        
        Args:
            market: Market pair (e.g., 'BTC_USDT')
            side: Order side ('buy' or 'sell')
            amount: Order amount in base currency
            price: Order price in quote currency
        """
        result = await self.client.call_tool(
            "create_limit_order",
            {
                "order": {
                    "market": market,
                    "side": side,
                    "amount": amount,
                    "price": price
                }
            }
        )
        return result.content[0].text

    async def create_stop_limit_order(
        self, market: str, side: str, amount: float, price: float, activation_price: float
    ) -> Dict:
        """Create a stop limit order
        
        Args:
            market: Market pair (e.g., 'BTC_USDT')
            side: Order side ('buy' or 'sell')
            amount: Order amount in base currency
            price: Order price in quote currency
            activation_price: Price at which the order will be activated
        """
        result = await self.client.call_tool(
            "create_stop_limit_order",
            {
                "order": {
                    "market": market,
                    "side": side,
                    "amount": amount,
                    "price": price,
                    "activation_price": activation_price
                }
            }
        )
        return result.content[0].text

    async def active_orders(self, market: Optional[str] = None) -> Dict:
        """Get active orders
        
        Args:
            market: Market pair (optional, if not provided returns orders for all markets)
        """
        params = {}
        if market:
            params["market"] = {"market": market}

        result = await self.client.call_tool("active_orders", params)
        return result.content[0].text

    async def cancel_order(self, order_id: int, market: str) -> Dict:
        """Cancel an order
        
        Args:
            order_id: Order ID
            market: Market pair
        """
        result = await self.client.call_tool(
            "cancel_order",
            {
                "order_id": order_id,
                "market": {"market": market}
            }
        )
        return result.content[0].text

    async def get_last_price(self, market: str) -> Dict:
        """Get last price for a specific market using WebSocket
        
        Args:
            market: Market pair (e.g., 'BTC_USDT')
        """
        result = await self.client.call_tool(
            "get_last_price",
            {
                "market": {"market": market}
            }
        )
        return result.content[0].text

    async def get_market_depth(self, market: str) -> Dict:
        """Get market depth for a specific market using WebSocket
        
        Args:
            market: Market pair (e.g., 'BTC_USDT')
        """
        result = await self.client.call_tool(
            "get_market_depth",
            {
                "market": {"market": market}
            }
        )
        return result.content[0].text

    async def get_markets_resource(self) -> Dict:
        """Get information about all available markets as a resource"""
        result = await self.client.read_resource("whitebit://markets")
        return result[0].content

    async def get_market_resource(self, market: str) -> Dict:
        """Get information about a specific market as a resource"""
        result = await self.client.read_resource(f"whitebit://markets/{market}")
        return result[0].content

    async def get_assets_resource(self) -> Dict:
        """Get status of all assets as a resource"""
        result = await self.client.read_resource("whitebit://assets")
        return result[0].content

    async def get_asset_resource(self, asset: str) -> Dict:
        """Get status of a specific asset as a resource"""
        result = await self.client.read_resource(f"whitebit://assets/{asset}")
        return result[0].content
