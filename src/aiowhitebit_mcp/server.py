"""WhiteBit MCP Server.

This module provides a WhiteBit MCP server that exposes WhiteBit API
functionality as MCP tools.
"""

import asyncio
import logging
import time
from typing import Optional

from aiowhitebit.clients.private import PrivateV4Client
from aiowhitebit.clients.public import PublicV1Client, PublicV2Client, PublicV4Client
from aiowhitebit.clients.websocket import PublicWebSocketClient
from fastmcp import FastMCP
from pydantic import BaseModel, Field

from aiowhitebit_mcp.metrics import get_metrics_collector, track_request
from aiowhitebit_mcp.monitoring import get_monitoring_server, register_health_check
from aiowhitebit_mcp.proxy import PrivateV4ClientProxy, PublicV1ClientProxy, PublicV2ClientProxy, PublicV4ClientProxy
from aiowhitebit_mcp.rate_limiter import configure_rate_limiter
from aiowhitebit_mcp.web_interface import start_web_interface, stop_web_interface

# Set up logging
logger = logging.getLogger(__name__)


class MarketPair(BaseModel):
    """Market pair model for MCP tools."""

    market: str = Field(..., description="Market pair (e.g., 'BTC_USDT')")


class OrderParams(BaseModel):
    """Parameters for creating an order."""

    market: str = Field(..., description="Market pair (e.g., 'BTC_USDT')")
    side: str = Field(..., description="Order side ('buy' or 'sell')")
    amount: float = Field(..., description="Order amount in base currency")
    price: float = Field(..., description="Order price in quote currency")


class StopOrderParams(OrderParams):
    """Parameters for creating a stop order.

    This model extends OrderParams to include the activation price parameter
    required for stop orders.

    Attributes:
        activation_price: The price at which the order will be activated
    """

    activation_price: float = Field(..., description="Price at which the order will be activated")


class WhiteBitMCP:
    """WhiteBit MCP Server.

    Provides MCP tools and resources for interacting with the WhiteBit cryptocurrency exchange.
    This class wraps the aiowhitebit library and exposes its functionality as MCP tools.

    The server supports both public and private API endpoints, as well as websocket connections.
    All public v4 client methods are wrapped and exposed as MCP tools, allowing for easy integration
    with MCP clients.
    """

    def __init__(
        self,
        name: str = "WhiteBit MCP",
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        web_interface: bool = False,
        web_host: str = "localhost",
        web_port: int = 8080,
    ):
        """Initialize the WhiteBit MCP server.

        This constructor initializes the MCP server with the given name and API credentials.
        It creates instances of the WhiteBit API clients and registers the MCP tools and resources.

        Args:
            name: Name of the MCP server
            api_key: WhiteBit API key (optional, required for private API access)
            api_secret: WhiteBit API secret (optional, required for private API access)
            web_interface: Whether to start the web interface
            web_host: Host to bind the web interface to
            web_port: Port to bind the web interface to
        """
        self.name = name
        self.api_key = api_key
        self.api_secret = api_secret
        self.web_interface = web_interface
        self.web_host = web_host
        self.web_port = web_port

        logger.info(f"Initializing {name} server")

        # Create FastMCP instance
        self.mcp = FastMCP(name=name)
        logger.debug("FastMCP instance created")

        # Configure rate limiter
        logger.debug("Configuring rate limiter")
        configure_rate_limiter()
        logger.debug("Rate limiter configured")

        # Initialize public clients
        logger.debug("Initializing public clients")
        # Create the original clients and wrap them with our proxies
        original_public_v1 = PublicV1Client()
        self.public_v1 = PublicV1ClientProxy(original_public_v1)

        original_public_v2 = PublicV2Client()
        self.public_v2 = PublicV2ClientProxy(original_public_v2)

        original_public_v4 = PublicV4Client()
        self.public_v4 = PublicV4ClientProxy(original_public_v4)
        logger.debug("Public clients initialized")

        # Initialize private client if credentials are provided
        self.private_v4 = None
        if api_key and api_secret:
            logger.debug("Initializing private client with provided credentials")
            original_private_v4 = PrivateV4Client(api_key=api_key, secret_key=api_secret)
            self.private_v4 = PrivateV4ClientProxy(original_private_v4)
            logger.debug("Private client initialized")
        else:
            logger.debug("No API credentials provided, private API access will be unavailable")

        # WebSocket client will be initialized on demand
        self.ws_client = None
        logger.debug("WebSocket client will be initialized on demand")

        # Register tools and resources
        logger.debug("Registering public tools")
        self._register_public_tools()

        if self.private_v4:
            logger.debug("Registering private tools")
            self._register_private_tools()
        else:
            logger.debug("Skipping private tools registration (no credentials provided)")

        # Register websocket tools
        logger.debug("Registering websocket tools")
        self._register_websocket_tools()

        # Register resources
        logger.debug("Registering resources")
        self._register_resources()

        # Set up monitoring
        logger.debug("Setting up monitoring")
        self._setup_monitoring()

        logger.info(f"{name} server initialized successfully")

    def _register_public_v1_tools(self):
        """Register public v1 API tools.

        This method registers all the public v1 API endpoints as MCP tools.
        It wraps the methods from the PublicV1Client and exposes them as
        MCP tools that can be called by MCP clients.
        """
        logger.debug("Registering public v1 API tools")

        @self.mcp.tool()
        async def get_ticker(market: MarketPair) -> dict:
            """Get ticker information for a specific market.

            Args:
                market: Market pair (e.g., 'BTC_USDT')
            """
            logger.debug(f"Tool call: get_ticker for {market.market}")
            result = await self.public_v1.get_ticker(market.market)
            logger.debug("get_ticker result received")
            return {"ticker": result.dict() if hasattr(result, "dict") else result}

        @self.mcp.tool()
        async def get_tickers() -> dict:
            """Get ticker information for all markets."""
            logger.debug("Tool call: get_tickers")
            result = await self.public_v1.get_tickers()
            logger.debug(f"get_tickers result: {len(result)} tickers")
            return {"tickers": result}

        logger.debug("Public v1 API tools registered successfully")

    def _register_public_v2_tools(self):
        """Register public v2 API tools.

        This method registers all the public v2 API endpoints as MCP tools.
        It wraps the methods from the PublicV2Client and exposes them as
        MCP tools that can be called by MCP clients.
        """
        logger.debug("Registering public v2 API tools")

        @self.mcp.tool()
        async def get_symbols() -> dict:
            """Get all available symbols."""
            logger.debug("Tool call: get_symbols")
            result = await self.public_v2.get_symbols()
            logger.debug(f"get_symbols result: {len(result)} symbols")
            return {"symbols": result}

        @self.mcp.tool()
        async def get_assets() -> dict:
            """Get all available assets."""
            logger.debug("Tool call: get_assets")
            result = await self.public_v2.get_assets()
            logger.debug(f"get_assets result: {len(result)} assets")
            return {"assets": result}

        logger.debug("Public v2 API tools registered successfully")

    def _register_public_v4_tools(self):
        """Register public v4 API tools.

        This method registers all the public v4 API endpoints as MCP tools.
        It wraps the methods from the PublicV4Client and exposes them as
        MCP tools that can be called by MCP clients.
        """
        logger.debug("Registering public v4 API tools")

        @track_request("get_server_time")
        @self.mcp.tool()
        async def get_server_time() -> dict:
            """Get current server time."""
            result = await self.public_v4.get_server_time()
            return {"time": result.model_dump() if hasattr(result, "model_dump") else result.model_dump()}

        @self.mcp.tool()
        async def get_server_status() -> dict:
            """Get current server status."""
            result = await self.public_v4.get_server_status()
            return {"status": result.model_dump() if hasattr(result, "model_dump") else result.dict()}

        @track_request("get_market_info")
        @self.mcp.tool()
        async def get_market_info() -> dict:
            """Get information about all available markets."""
            result = await self.public_v4.get_market_info()
            return {"markets": list(result)}  # Convert MarketInfo to a regular list and wrap in dict

        @self.mcp.tool()
        async def get_market_activity() -> dict:
            """Get activity information for all markets (last price, volume, etc.)."""
            result = await self.public_v4.get_market_activity()
            return {"activities": list(result)}  # Convert MarketActivity to a regular list and wrap in dict

        @self.mcp.tool()
        async def get_orderbook(market: MarketPair) -> dict:
            """Get orderbook for a specific market.

            Args:
                market: Market pair (e.g., 'BTC_USDT')
            """
            result = await self.public_v4.get_orderbook(market.market)
            return {"orderbook": result.model_dump() if hasattr(result, "model_dump") else result.dict()}

        @self.mcp.tool()
        async def get_recent_trades(market: MarketPair) -> dict:
            """Get recent trades for a specific market.

            Args:
                market: Market pair (e.g., 'BTC_USDT')
            """
            result = await self.public_v4.get_recent_trades(market.market)
            return {"trades": list(result)}  # Convert RecentTrades to a regular list and wrap in dict

        @self.mcp.tool()
        async def get_fee(market: MarketPair) -> dict:
            """Get trading fee for a specific market.

            Args:
                market: Market pair (e.g., 'BTC_USDT')
            """
            result = await self.public_v4.get_fee(market.market)
            return {"fee": result.model_dump() if hasattr(result, "model_dump") else result.dict()}

        @self.mcp.tool()
        async def get_asset_status_list() -> dict:
            """Get status of all assets."""
            result = await self.public_v4.get_asset_status_list()
            return {"assets": list(result)}  # Convert AssetStatus to a regular list and wrap in dict

        @self.mcp.tool()
        async def get_kline(market: MarketPair, interval: str, start_time: int, end_time: int) -> dict:
            """Get kline (candlestick) data for a specific market.

            Args:
                market: Market pair (e.g., 'BTC_USDT')
                interval: Kline interval (e.g., '1m', '1h', '1d')
                start_time: Start time in seconds
                end_time: End time in seconds
            """
            logger.debug(
                f"Tool call: get_kline for {market.market} with "
                f"interval={interval}, start_time={start_time}, end_time={end_time}"
            )
            result = await self.public_v4.get_kline(market.market, interval, start_time, end_time)
            logger.debug(f"get_kline result: {len(result)} klines")
            return {"klines": list(result)}  # Convert Kline to a regular list and wrap in dict

        logger.debug("Public v4 API tools registered successfully")

    def _register_public_tools(self):
        """Register all public API tools.

        This method is a convenience method that registers all public API tools
        by calling the individual registration methods for each API version.
        """
        logger.debug("Registering all public API tools")
        self._register_public_v1_tools()
        self._register_public_v2_tools()
        self._register_public_v4_tools()
        logger.debug("All public API tools registered successfully")

    def _register_private_tools(self):
        """Register private API tools.

        This method registers all the private API endpoints as MCP tools.
        It wraps the methods from the PrivateV4Client and exposes them as
        MCP tools that can be called by MCP clients.

        Note: This method is only called if API credentials are provided.
        """
        if not self.private_v4:
            logger.warning("Cannot register private API tools: no API credentials provided")
            return

        logger.debug("Registering private API tools")

        @track_request("get_trading_balance")
        @self.mcp.tool()
        async def get_trading_balance() -> dict:
            """Get trading balance for all assets."""
            logger.debug("Tool call: get_trading_balance")
            result = await self.private_v4.get_trading_balance()
            logger.debug("get_trading_balance result received")
            return {"balance": result}

        @track_request("create_limit_order")
        @self.mcp.tool()
        async def create_limit_order(order: OrderParams) -> dict:
            """Create a limit order.

            Args:
                order: Order parameters
            """
            logger.debug(f"Tool call: create_limit_order for {order.market}")
            result = await self.private_v4.create_limit_order(
                market=order.market, side=order.side, amount=str(order.amount), price=str(order.price)
            )
            logger.debug(f"create_limit_order result: {result}")
            return {"order": result}

        @track_request("cancel_order")
        @self.mcp.tool()
        async def cancel_order(order_id: int, market: MarketPair) -> dict:
            """Cancel an order.

            Args:
                order_id: Order ID to cancel
                market: Market pair (e.g., 'BTC_USDT')
            """
            logger.debug(f"Tool call: cancel_order for order {order_id} in {market.market}")
            result = await self.private_v4.cancel_order(order_id, market.market)
            logger.debug(f"cancel_order result: {result}")
            return {"order": result}

        @track_request("get_order_status")
        @self.mcp.tool()
        async def get_order_status(order_id: int, market: MarketPair) -> dict:
            """Get order status.

            Args:
                order_id: Order ID to check
                market: Market pair (e.g., 'BTC_USDT')
            """
            logger.debug(f"Tool call: get_order_status for order {order_id} in {market.market}")
            result = await self.private_v4.get_order_status(order_id, market.market)
            logger.debug(f"get_order_status result: {result}")
            return {"order": result}

        @track_request("get_active_orders")
        @self.mcp.tool()
        async def get_active_orders(market: MarketPair) -> dict:
            """Get active orders for a market.

            Args:
                market: Market pair (e.g., 'BTC_USDT')
            """
            logger.debug(f"Tool call: get_active_orders for {market.market}")
            result = await self.private_v4.get_active_orders(market.market)
            logger.debug(f"get_active_orders result: {len(result)} orders")
            return {"orders": result}

        logger.debug("Private API tools registered successfully")

    def _register_websocket_tools(self):
        """Register WebSocket tools.

        This method registers all the WebSocket endpoints as MCP tools.
        It wraps the methods from the WebSocketClient and exposes them as
        MCP tools that can be called by MCP clients.
        """
        logger.debug("Registering WebSocket tools")

        @self.mcp.tool()
        async def connect_websocket() -> dict:
            """Connect to the WebSocket API."""
            if not self.ws_client:
                logger.debug("Initializing WebSocket client")
                self.ws_client = PublicWebSocketClient()
                logger.debug("WebSocket client initialized")

            logger.debug("Connecting to WebSocket")
            await self.ws_client.connect()
            logger.debug("Connected to WebSocket")

            return {"status": "connected"}

        @self.mcp.tool()
        async def disconnect_websocket() -> dict:
            """Disconnect from the WebSocket API."""
            if not self.ws_client:
                logger.warning("WebSocket client not initialized")
                return {"status": "not_connected"}

            logger.debug("Disconnecting from WebSocket")
            await self.ws_client.disconnect()
            logger.debug("Disconnected from WebSocket")

            return {"status": "disconnected"}

        logger.debug("WebSocket tools registered successfully")

    def _setup_monitoring(self):
        """Set up monitoring for the WhiteBit MCP server.

        This method sets up monitoring for the WhiteBit MCP server, including
        health checks and metrics collection.
        """
        logger.debug("Setting up health checks")
        monitoring_server = get_monitoring_server(f"{self.name} Monitoring")

        # Register health checks
        async def check_public_v4_api():
            try:
                start_time = time.time()
                result = await self.public_v4.get_server_time()
                duration = time.time() - start_time
                return {
                    "duration": duration,
                    "server_time": result.model_dump() if hasattr(result, "model_dump") else result.dict(),
                }
            except Exception as e:
                raise Exception(f"Public v4 API health check failed: {e}") from e

        register_health_check("public_v4_api", check_public_v4_api)

        # Register metrics collector
        self.metrics_collector = get_metrics_collector()

        # Start web interface if enabled
        if self.web_interface:
            logger.debug(f"Starting web interface on http://{self.web_host}:{self.web_port}")
            asyncio.create_task(start_web_interface(host=self.web_host, port=self.web_port))

        # Register monitoring tools
        @self.mcp.tool()
        async def health() -> dict:
            """Get the health status of the WhiteBit MCP server."""
            return await monitoring_server.health_check.run_checks()

        @self.mcp.tool()
        async def metrics() -> dict:
            """Get metrics for the WhiteBit MCP server."""
            return self.metrics_collector.get_summary()

        @self.mcp.tool()
        async def reset_metrics() -> dict:
            """Reset all metrics."""
            self.metrics_collector.reset()
            return {"status": "ok", "message": "Metrics reset successfully"}

        @self.mcp.tool()
        async def circuit_breakers() -> dict:
            """Get the status of all circuit breakers."""
            from aiowhitebit_mcp.circuit_breaker import get_all_circuit_breakers

            result = {}
            for name, circuit in get_all_circuit_breakers().items():
                result[name] = circuit.get_state()
            return result

        @self.mcp.tool()
        async def reset_circuit_breaker(name: str) -> dict:
            """Reset a circuit breaker.

            Args:
                name: The name of the circuit breaker to reset
            """
            from aiowhitebit_mcp.circuit_breaker import reset_circuit_breaker as reset_cb

            success = reset_cb(name)
            if success:
                return {"status": "ok", "message": f"Circuit breaker {name} reset successfully"}
            else:
                return {"status": "error", "message": f"Circuit breaker {name} not found"}

        logger.debug("Monitoring setup complete")

    def _register_resources(self):
        """Register resources."""

        @self.mcp.resource("whitebit://markets")
        async def get_markets_resource() -> dict:
            """Get information about all available markets."""
            result = await self.public_v4.get_market_info()
            return {"markets": list(result)}

        @self.mcp.resource("whitebit://assets")
        async def get_assets_resource() -> dict:
            """Get information about all available assets."""
            result = await self.public_v2.get_assets()
            return {"assets": result}

    async def close(self):
        """Close the server and release resources.

        This method should be called when the server is no longer needed to ensure
        proper cleanup of resources. It closes all API clients and releases any
        other resources held by the server.
        """
        logger.info(f"Closing {self.name} server")

        # Close public clients
        logger.debug("Closing public clients")
        await self.public_v1.close()
        await self.public_v2.close()
        await self.public_v4.close()
        logger.debug("Public clients closed")

        # Close private client if it exists
        if self.private_v4:
            logger.debug("Closing private client")
            await self.private_v4.close()
            logger.debug("Private client closed")

        # Close websocket client if it exists
        if self.ws_client:
            logger.debug("Closing websocket client")
            await self.ws_client.close()
            logger.debug("Websocket client closed")

        # Stop web interface if it was started
        if self.web_interface:
            logger.debug("Stopping web interface")
            await stop_web_interface()
            logger.debug("Web interface stopped")

        logger.info(f"{self.name} server closed successfully")


def create_server(
    name: str = "WhiteBit MCP",
    api_key: Optional[str] = None,
    api_secret: Optional[str] = None,
    web_interface: bool = False,
    web_host: str = "localhost",
    web_port: int = 8080,
) -> WhiteBitMCP:
    """Create a new WhiteBit MCP server instance.

    Args:
        name: Name of the MCP server
        api_key: WhiteBit API key for private endpoints
        api_secret: WhiteBit API secret for private endpoints
        web_interface: Whether to enable the web interface
        web_host: Host to bind the web interface to
        web_port: Port to bind the web interface to

    Returns:
        A new WhiteBit MCP server instance
    """
    logger.info(f"Creating new WhiteBit MCP server: {name}")
    return WhiteBitMCP(
        name=name,
        api_key=api_key,
        api_secret=api_secret,
        web_interface=web_interface,
        web_host=web_host,
        web_port=web_port,
    )
