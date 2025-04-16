"""WhiteBit MCP Server - Provides MCP tools and resources for interacting with the WhiteBit cryptocurrency exchange.
"""

from typing import Dict, Optional

from aiowhitebit.clients.private import PrivateV4Client
from aiowhitebit.clients.public import PublicV1Client, PublicV2Client, PublicV4Client
from aiowhitebit.clients.websocket import get_public_websocket_client
from aiowhitebit.models import TradingBalanceItem, TradingBalanceList, CreateOrderResponse, CancelOrderResponse, \
    WSResponse
from aiowhitebit.models.public.v4 import MarketInfo, ServerTime, ServerStatus, Orderbook, RecentTrades
from fastmcp import Context, FastMCP
from pydantic import BaseModel, Field


class MarketPair(BaseModel):
    """Market pair for trading (e.g., 'BTC_USDT')"""
    market: str = Field(..., description="Market pair in format 'BASE_QUOTE' (e.g., 'BTC_USDT')")


class OrderParams(BaseModel):
    """Parameters for creating an order"""
    market: str = Field(..., description="Market pair in format 'BASE_QUOTE' (e.g., 'BTC_USDT')")
    side: str = Field(..., description="Order side: 'buy' or 'sell'")
    amount: float = Field(..., description="Order amount in base currency")
    price: float = Field(..., description="Order price in quote currency")


class StopOrderParams(OrderParams):
    """Parameters for creating a stop order"""
    activation_price: float = Field(..., description="Price at which the order will be activated")


class WhiteBitMCP:
    """WhiteBit MCP Server class"""

    def __init__(
        self,
        name: str = "WhiteBit MCP",
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None
    ):
        """Initialize the WhiteBit MCP server.
        
        Args:
            name: Name of the MCP server
            api_key: WhiteBit API key for private endpoints (optional)
            api_secret: WhiteBit API secret for private endpoints (optional)
        """
        self.mcp = FastMCP(name)

        # Initialize public clients
        self.public_v1 = PublicV1Client()
        self.public_v2 = PublicV2Client()
        self.public_v4 = PublicV4Client()

        # Initialize private client if credentials are provided
        self.private_v4 = None
        if api_key and api_secret:
            self.private_v4 = PrivateV4Client(api_key=api_key, secret_key=api_secret)

        # WebSocket client will be initialized on demand
        self.ws_client = None

        # Register tools and resources
        self._register_public_tools()
        self._register_private_tools()
        self._register_websocket_tools()
        self._register_resources()

    def _register_public_tools(self):
        """Register public API tools"""

        @self.mcp.tool()
        async def get_market_info() -> MarketInfo:
            """Get information about all available markets"""
            return await self.public_v4.get_market_info()

        @self.mcp.tool()
        async def get_market_activity() -> Dict:
            """Get activity information for all markets (last price, volume, etc.)"""
            return await self.public_v4.get_market_activity()

        @self.mcp.tool()
        async def get_server_time() -> ServerTime:
            """Get current server time"""
            return await self.public_v4.get_server_time()

        @self.mcp.tool()
        async def get_server_status() -> ServerStatus:
            """Get current server status"""
            return await self.public_v4.get_server_status()

        @self.mcp.tool()
        async def get_asset_status_list() -> Dict:
            """Get status of all assets"""
            return await self.public_v4.get_asset_status_list()

        @self.mcp.tool()
        async def get_orderbook(market: MarketPair, limit: int = 100, level: int = 0) -> Orderbook:
            """Get orderbook for a specific market
            
            Args:
                market: Market pair (e.g., 'BTC_USDT')
                limit: Number of orders to return (default: 100)
                level: Aggregation level (default: 0)
            """
            return await self.public_v4.get_orderbook(
                market=market.market,
                limit=limit,
                level=level
            )

        @self.mcp.tool()
        async def get_recent_trades(market: MarketPair, limit: int = 100) -> RecentTrades:
            """Get recent trades for a specific market
            
            Args:
                market: Market pair (e.g., 'BTC_USDT')
                limit: Number of trades to return (default: 100)
            """
            return await self.public_v4.get_recent_trades(
                market=market.market,
                limit=limit
            )

        @self.mcp.tool()
        async def get_fee(market: MarketPair) -> Dict:
            """Get trading fee for a specific market
            
            Args:
                market: Market pair (e.g., 'BTC_USDT')
            """
            return await self.public_v4.get_fee(market=market.market)

    def _register_private_tools(self):
        """Register private API tools (if credentials are provided)"""
        if not self.private_v4:
            return

        @self.mcp.tool()
        async def get_trading_balance() -> TradingBalanceItem | TradingBalanceList:
            """Get trading balance for all assets"""
            return await self.private_v4.get_trading_balance()

        @self.mcp.tool()
        async def create_limit_order(order: OrderParams) -> CreateOrderResponse:
            """Create a limit order
            
            Args:
                order: Order parameters
            """
            return await self.private_v4.create_limit_order(
                market=order.market,
                side=order.side,
                amount=str(order.amount),
                price=str(order.price)
            )

        @self.mcp.tool()
        async def create_stop_limit_order(order: StopOrderParams) -> CreateOrderResponse:
            """Create a stop limit order
            
            Args:
                order: Stop order parameters
            """
            return await self.private_v4.create_stop_limit_order(
                market=order.market,
                side=order.side,
                amount=str(order.amount),
                price=str(order.price),
                activation_price=str(order.activation_price)
            )

        @self.mcp.tool()
        async def active_orders(market: Optional[MarketPair] = None) -> list[CreateOrderResponse]:
            """Get active orders
            
            Args:
                market: Market pair (optional, if not provided returns orders for all markets)
            """
            market_str = market.market if market else None
            return await self.private_v4.active_orders(market=market_str)

        @self.mcp.tool()
        async def cancel_order(order_id: int, market: MarketPair) -> CancelOrderResponse:
            """Cancel an order
            
            Args:
                order_id: Order ID
                market: Market pair
            """
            return await self.private_v4.cancel_order(
                order_id=order_id,
                market=market.market
            )

    def _register_websocket_tools(self):
        """Register WebSocket tools"""

        @self.mcp.tool()
        async def get_last_price(market: MarketPair, ctx: Context) -> WSResponse:
            """Get last price for a specific market using WebSocket
            
            Args:
                market: Market pair (e.g., 'BTC_USDT')
            """
            await ctx.info(f"Fetching last price for {market.market}...")

            # Initialize WebSocket client if needed
            if not self.ws_client:
                self.ws_client = get_public_websocket_client()

            result = await self.ws_client.last_price(market.market)
            await ctx.info(f"Received last price data for {market.market}")
            return result

        @self.mcp.tool()
        async def get_market_depth(market: MarketPair, ctx: Context) -> WSResponse:
            """Get market depth for a specific market using WebSocket
            
            Args:
                market: Market pair (e.g., 'BTC_USDT')
            """
            await ctx.info(f"Fetching market depth for {market.market}...")

            # Initialize WebSocket client if needed
            if not self.ws_client:
                self.ws_client = get_public_websocket_client()

            result = await self.ws_client.market_depth(market.market)
            await ctx.info(f"Received market depth data for {market.market}")
            return result

    def _register_resources(self):
        """Register resources"""

        @self.mcp.resource("whitebit://markets")
        async def get_markets_resource() -> MarketInfo:
            """Get information about all available markets"""
            return await self.public_v4.get_market_info()

        @self.mcp.resource("whitebit://markets/{market}")
        async def get_market_resource(market: str) -> Dict:
            """Get information about a specific market"""
            all_markets = await self.public_v4.get_market_info()
            if market in all_markets:
                return {market: all_markets[market]}
            return {"error": f"Market {market} not found"}

        @self.mcp.resource("whitebit://assets")
        async def get_assets_resource() -> Dict:
            """Get status of all assets"""
            return await self.public_v4.get_asset_status_list()

        @self.mcp.resource("whitebit://assets/{asset}")
        async def get_asset_resource(asset: str) -> Dict:
            """Get status of a specific asset"""
            all_assets = await self.public_v4.get_asset_status_list()
            for asset_data in all_assets:
                if asset_data.get("name") == asset:
                    return asset_data
            return {"error": f"Asset {asset} not found"}

    def run(self, **kwargs):
        """Run the MCP server"""
        return self.mcp.run(**kwargs)

    async def close(self):
        """Close all clients"""
        await self.public_v1.close()
        await self.public_v2.close()
        await self.public_v4.close()

        if self.private_v4:
            await self.private_v4.close()

        if self.ws_client:
            await self.ws_client.close()


def create_server(
    name: str = "WhiteBit MCP",
    api_key: Optional[str] = None,
    api_secret: Optional[str] = None
) -> WhiteBitMCP:
    """Create a WhiteBit MCP server
    
    Args:
        name: Name of the MCP server
        api_key: WhiteBit API key for private endpoints (optional)
        api_secret: WhiteBit API secret for private endpoints (optional)
    
    Returns:
        WhiteBitMCP: The MCP server instance
    """
    return WhiteBitMCP(name=name, api_key=api_key, api_secret=api_secret)
