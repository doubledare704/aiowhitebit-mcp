"""Multi-exchange MCP Server.

This module provides a multi-exchange MCP server that supports multiple
cryptocurrency exchanges.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Union

from fastmcp import FastMCP
from pydantic import BaseModel, Field

from aiowhitebit_mcp.exchange import Exchange, ExchangeType, create_exchange
from aiowhitebit_mcp.metrics import track_request, get_metrics_collector
from aiowhitebit_mcp.monitoring import get_monitoring_server, register_health_check
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


class ExchangeParams(BaseModel):
    """Parameters for specifying an exchange."""
    exchange: ExchangeType = Field(..., description="Exchange type")


class MultiExchangeMCP:
    """Multi-exchange MCP Server.
    
    Provides MCP tools and resources for interacting with multiple cryptocurrency exchanges.
    This class wraps the exchange abstraction layer and exposes its functionality as MCP tools.
    
    The server supports multiple exchanges and provides a consistent interface for all of them.
    """
    
    def __init__(
        self,
        name: str = "Multi-Exchange MCP",
        exchanges: Optional[Dict[ExchangeType, Dict[str, str]]] = None,
        default_exchange: ExchangeType = ExchangeType.WHITEBIT,
        web_interface: bool = False,
        web_host: str = "localhost",
        web_port: int = 8080
    ):
        """Initialize the multi-exchange MCP server.

        This constructor initializes the MCP server with the given name and exchange credentials.
        It creates instances of the exchange clients and registers the MCP tools and resources.

        Args:
            name: Name of the MCP server
            exchanges: Dictionary mapping exchange types to credential dictionaries
                (e.g., {ExchangeType.WHITEBIT: {"api_key": "...", "api_secret": "..."}})
            default_exchange: Default exchange to use when no exchange is specified
            web_interface: Whether to start the web interface
            web_host: Host to bind the web interface to
            web_port: Port to bind the web interface to
        """
        self.name = name
        self.exchanges = {}
        self.default_exchange = default_exchange
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

        # Initialize exchanges
        logger.debug("Initializing exchanges")
        if exchanges:
            for exchange_type, credentials in exchanges.items():
                self._add_exchange(
                    exchange_type,
                    credentials.get("api_key"),
                    credentials.get("api_secret")
                )
        else:
            # Add default exchange with no credentials
            self._add_exchange(default_exchange)
        logger.debug("Exchanges initialized")

        # Register tools and resources
        logger.debug("Registering tools")
        self._register_tools()
        logger.debug("Tools registered")

        # Register resources
        logger.debug("Registering resources")
        self._register_resources()
        logger.debug("Resources registered")
        
        # Set up monitoring
        logger.debug("Setting up monitoring")
        self._setup_monitoring()
        logger.debug("Monitoring setup complete")
        
        logger.info(f"{name} server initialized successfully")
    
    def _add_exchange(
        self,
        exchange_type: ExchangeType,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None
    ) -> None:
        """Add an exchange to the server.
        
        Args:
            exchange_type: Type of exchange to add
            api_key: API key for the exchange (optional, required for private API access)
            api_secret: API secret for the exchange (optional, required for private API access)
        """
        logger.debug(f"Adding exchange: {exchange_type}")
        self.exchanges[exchange_type] = create_exchange(
            exchange_type=exchange_type,
            api_key=api_key,
            api_secret=api_secret
        )
        logger.debug(f"Exchange {exchange_type} added")
    
    def _get_exchange(self, exchange_type: Optional[ExchangeType] = None) -> Exchange:
        """Get an exchange instance.
        
        Args:
            exchange_type: Type of exchange to get (optional, defaults to default_exchange)
            
        Returns:
            Exchange: The exchange instance
            
        Raises:
            ValueError: If the exchange type is not supported or not initialized
        """
        exchange_type = exchange_type or self.default_exchange
        
        if exchange_type not in self.exchanges:
            raise ValueError(f"Exchange {exchange_type} not initialized")
        
        return self.exchanges[exchange_type]
    
    def _register_tools(self):
        """Register MCP tools.
        
        This method registers all the exchange endpoints as MCP tools.
        It wraps the methods from the Exchange interface and exposes them as
        MCP tools that can be called by MCP clients.
        """
        logger.debug("Registering exchange tools")

        @self.mcp.tool()
        @track_request("get_server_time")
        async def get_server_time(exchange: Optional[ExchangeParams] = None) -> Dict:
            """Get current server time
            
            Args:
                exchange: Exchange parameters (optional, defaults to default exchange)
            """
            exchange_type = exchange.exchange if exchange else None
            result = await self._get_exchange(exchange_type).get_server_time()
            return {"time": result}

        @self.mcp.tool()
        async def get_server_status(exchange: Optional[ExchangeParams] = None) -> Dict:
            """Get current server status
            
            Args:
                exchange: Exchange parameters (optional, defaults to default exchange)
            """
            exchange_type = exchange.exchange if exchange else None
            result = await self._get_exchange(exchange_type).get_server_status()
            return {"status": result}

        @self.mcp.tool()
        @track_request("get_market_info")
        async def get_market_info(exchange: Optional[ExchangeParams] = None) -> Dict:
            """Get information about all available markets
            
            Args:
                exchange: Exchange parameters (optional, defaults to default exchange)
            """
            exchange_type = exchange.exchange if exchange else None
            result = await self._get_exchange(exchange_type).get_market_info()
            return {"markets": result}

        @self.mcp.tool()
        async def get_orderbook(market: MarketPair, exchange: Optional[ExchangeParams] = None) -> Dict:
            """Get orderbook for a specific market
            
            Args:
                market: Market pair (e.g., 'BTC_USDT')
                exchange: Exchange parameters (optional, defaults to default exchange)
            """
            exchange_type = exchange.exchange if exchange else None
            result = await self._get_exchange(exchange_type).get_orderbook(market.market)
            return {"orderbook": result}

        @self.mcp.tool()
        async def get_recent_trades(market: MarketPair, exchange: Optional[ExchangeParams] = None) -> Dict:
            """Get recent trades for a specific market
            
            Args:
                market: Market pair (e.g., 'BTC_USDT')
                exchange: Exchange parameters (optional, defaults to default exchange)
            """
            exchange_type = exchange.exchange if exchange else None
            result = await self._get_exchange(exchange_type).get_recent_trades(market.market)
            return {"trades": result}

        @self.mcp.tool()
        async def get_kline(
            market: MarketPair,
            interval: str,
            start_time: int,
            end_time: int,
            exchange: Optional[ExchangeParams] = None
        ) -> Dict:
            """Get kline (candlestick) data for a specific market
            
            Args:
                market: Market pair (e.g., 'BTC_USDT')
                interval: Kline interval (e.g., '1m', '1h', '1d')
                start_time: Start time in seconds
                end_time: End time in seconds
                exchange: Exchange parameters (optional, defaults to default exchange)
            """
            exchange_type = exchange.exchange if exchange else None
            result = await self._get_exchange(exchange_type).get_kline(
                market.market, interval, start_time, end_time
            )
            return {"klines": result}

        @self.mcp.tool()
        @track_request("get_trading_balance")
        async def get_trading_balance(exchange: Optional[ExchangeParams] = None) -> Dict:
            """Get trading balance for all assets
            
            Args:
                exchange: Exchange parameters (optional, defaults to default exchange)
            """
            exchange_type = exchange.exchange if exchange else None
            result = await self._get_exchange(exchange_type).get_trading_balance()
            return {"balance": result}

        @self.mcp.tool()
        @track_request("create_limit_order")
        async def create_limit_order(
            order: OrderParams,
            exchange: Optional[ExchangeParams] = None
        ) -> Dict:
            """Create a limit order
            
            Args:
                order: Order parameters
                exchange: Exchange parameters (optional, defaults to default exchange)
            """
            exchange_type = exchange.exchange if exchange else None
            result = await self._get_exchange(exchange_type).create_limit_order(
                market=order.market,
                side=order.side,
                amount=str(order.amount),
                price=str(order.price)
            )
            return {"order": result}
            
        @self.mcp.tool()
        @track_request("cancel_order")
        async def cancel_order(
            order_id: Union[int, str],
            market: MarketPair,
            exchange: Optional[ExchangeParams] = None
        ) -> Dict:
            """Cancel an order
            
            Args:
                order_id: Order ID to cancel
                market: Market pair (e.g., 'BTC_USDT')
                exchange: Exchange parameters (optional, defaults to default exchange)
            """
            exchange_type = exchange.exchange if exchange else None
            result = await self._get_exchange(exchange_type).cancel_order(
                order_id, market.market
            )
            return {"order": result}
            
        @self.mcp.tool()
        @track_request("get_order_status")
        async def get_order_status(
            order_id: Union[int, str],
            market: MarketPair,
            exchange: Optional[ExchangeParams] = None
        ) -> Dict:
            """Get order status
            
            Args:
                order_id: Order ID to check
                market: Market pair (e.g., 'BTC_USDT')
                exchange: Exchange parameters (optional, defaults to default exchange)
            """
            exchange_type = exchange.exchange if exchange else None
            result = await self._get_exchange(exchange_type).get_order_status(
                order_id, market.market
            )
            return {"order": result}
            
        @self.mcp.tool()
        @track_request("get_active_orders")
        async def get_active_orders(
            market: MarketPair,
            exchange: Optional[ExchangeParams] = None
        ) -> Dict:
            """Get active orders for a market
            
            Args:
                market: Market pair (e.g., 'BTC_USDT')
                exchange: Exchange parameters (optional, defaults to default exchange)
            """
            exchange_type = exchange.exchange if exchange else None
            result = await self._get_exchange(exchange_type).get_active_orders(
                market.market
            )
            return {"orders": result}
        
        @self.mcp.tool()
        async def list_exchanges() -> Dict:
            """List all available exchanges"""
            return {"exchanges": list(self.exchanges.keys())}
            
        logger.debug("Exchange tools registered successfully")
    
    def _register_resources(self):
        """Register resources"""

        @self.mcp.resource("exchange://markets")
        async def get_markets_resource() -> Dict:
            """Get information about all available markets"""
            result = await self._get_exchange().get_market_info()
            return {"markets": result}
        
        @self.mcp.resource("exchange://exchanges")
        async def get_exchanges_resource() -> Dict:
            """Get information about all available exchanges"""
            return {"exchanges": list(self.exchanges.keys())}
    
    def _setup_monitoring(self):
        """Set up monitoring for the multi-exchange MCP server.
        
        This method sets up monitoring for the multi-exchange MCP server, including
        health checks and metrics collection.
        """
        logger.debug("Setting up health checks")
        monitoring_server = get_monitoring_server(f"{self.name} Monitoring")
        
        # Register health checks for each exchange
        for exchange_type, exchange in self.exchanges.items():
            async def check_exchange_api(exchange_type=exchange_type, exchange=exchange):
                try:
                    start_time = time.time()
                    result = await exchange.get_server_time()
                    duration = time.time() - start_time
                    return {
                        "duration": duration,
                        "server_time": result
                    }
                except Exception as e:
                    raise Exception(f"{exchange_type} API health check failed: {e}")
            
            register_health_check(f"{exchange_type}_api", check_exchange_api)
        
        # Register metrics collector
        self.metrics_collector = get_metrics_collector()
        
        # Start web interface if enabled
        if self.web_interface:
            logger.debug(f"Starting web interface on http://{self.web_host}:{self.web_port}")
            asyncio.create_task(start_web_interface(host=self.web_host, port=self.web_port))
        
        # Register monitoring tools
        @self.mcp.tool()
        async def health() -> Dict:
            """Get the health status of the multi-exchange MCP server."""
            return await monitoring_server.health_check.run_checks()
        
        @self.mcp.tool()
        async def metrics() -> Dict:
            """Get metrics for the multi-exchange MCP server."""
            return self.metrics_collector.get_summary()
        
        @self.mcp.tool()
        async def reset_metrics() -> Dict:
            """Reset all metrics."""
            self.metrics_collector.reset()
            return {"status": "ok", "message": "Metrics reset successfully"}
        
        @self.mcp.tool()
        async def circuit_breakers() -> Dict:
            """Get the status of all circuit breakers."""
            from aiowhitebit_mcp.circuit_breaker import get_all_circuit_breakers
            result = {}
            for name, circuit in get_all_circuit_breakers().items():
                result[name] = circuit.get_state()
            return result
        
        @self.mcp.tool()
        async def reset_circuit_breaker(name: str) -> Dict:
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
    
    async def close(self):
        """Close the server and release resources.
        
        This method should be called when the server is no longer needed to ensure
        proper cleanup of resources. It closes all exchange clients and releases any
        other resources held by the server.
        """
        logger.info(f"Closing {self.name} server")
        
        # Close all exchanges
        for exchange_type, exchange in self.exchanges.items():
            logger.debug(f"Closing {exchange_type} exchange")
            await exchange.close()
            logger.debug(f"{exchange_type} exchange closed")
        
        # Stop web interface if it was started
        if self.web_interface:
            logger.debug("Stopping web interface")
            await stop_web_interface()
            logger.debug("Web interface stopped")
            
        logger.info(f"{self.name} server closed successfully")


def create_server(
    name: str = "Multi-Exchange MCP",
    exchanges: Optional[Dict[ExchangeType, Dict[str, str]]] = None,
    default_exchange: ExchangeType = ExchangeType.WHITEBIT,
    web_interface: bool = False,
    web_host: str = "localhost",
    web_port: int = 8080
) -> MultiExchangeMCP:
    """Create a new multi-exchange MCP server.

    This is a convenience function for creating a new multi-exchange MCP server instance.
    It initializes the server with the given name and exchange credentials.

    Args:
        name: Name of the MCP server
        exchanges: Dictionary mapping exchange types to credential dictionaries
            (e.g., {ExchangeType.WHITEBIT: {"api_key": "...", "api_secret": "..."}})
        default_exchange: Default exchange to use when no exchange is specified
        web_interface: Whether to start the web interface
        web_host: Host to bind the web interface to
        web_port: Port to bind the web interface to

    Returns:
        MultiExchangeMCP: A new multi-exchange MCP server instance ready to use
    """
    logger.info(f"Creating new multi-exchange MCP server: {name}")
    return MultiExchangeMCP(
        name=name,
        exchanges=exchanges,
        default_exchange=default_exchange,
        web_interface=web_interface,
        web_host=web_host,
        web_port=web_port
    )
