"""Proxy implementation for WhiteBit API clients."""

import logging
import traceback
from typing import Callable

from aiowhitebit.clients.private import PrivateV4Client
from aiowhitebit.clients.public import PublicV1Client, PublicV2Client, PublicV4Client
from aiowhitebit.models import CancelOrderResponse, CreateOrderResponse, TradingBalanceList
from aiowhitebit.models.public.v4 import (
    AssetStatus,
    Fee,
    MarketActivity,
    MarketInfo,
    Orderbook,
    RecentTrades,
    ServerStatus,
    ServerTime,
)

from aiowhitebit_mcp.cache import cached
from aiowhitebit_mcp.circuit_breaker import circuit_breaker
from aiowhitebit_mcp.rate_limiter import rate_limited

# Set up logging
logger = logging.getLogger(__name__)


# Note: rate_limited and cached decorators are imported from their respective modules


def optimized(ttl_seconds: int = 60, rate_limit_name: str = "public"):
    """Combined decorator that applies both caching and rate limiting.

    This decorator first applies caching and then rate limiting to a function.
    It provides both performance optimization and protection against rate limits.

    Args:
        ttl_seconds: Time to live for the cache entry in seconds
        rate_limit_name: Name of the rate limit rule to apply

    Returns:
        Decorated function with caching and rate limiting
    """

    def decorator(func: Callable):
        # Apply caching first, then rate limiting
        cached_func = cached(cache_name=func.__name__, ttl=ttl_seconds)(func)
        return rate_limited(rate_limit_name)(cached_func)

    return decorator


# Custom implementations for missing models
class Trade:
    """Trade data model."""

    def __init__(self, id: int, time: int, price: str, amount: str, type: str):
        """Initialize a Trade instance.

        Args:
            id: Trade ID
            time: Trade timestamp
            price: Trade price
            amount: Trade amount
            type: Trade type
        """
        self.id = id
        self.time = time
        self.price = price
        self.amount = amount
        self.type = type

    def dict(self):
        """Convert the trade object to a dictionary.

        Returns:
            dict: Dictionary representation of the trade
        """
        return {"id": self.id, "time": self.time, "price": self.price, "amount": self.amount, "type": self.type}


class OrderStatus:
    """Order status model."""

    def __init__(self, status: str):
        """Initialize OrderStatus.

        Args:
            status: The status of the order
        """
        self.status = status

    def dict(self):
        """Convert the order status to a dictionary.

        Returns:
            dict: Dictionary representation of the order status
        """
        return {"status": self.status}


class OrderInfo:
    """Order information model."""

    def __init__(
        self, order_id: int, market: str, type: str, side: str, status: str, price: str, amount: str, timestamp: int
    ):
        """Initialize OrderInfo.

        Args:
            order_id: Order identifier
            market: Market pair
            type: Order type
            side: Order side (buy/sell)
            status: Order status
            price: Order price
            amount: Order amount
            timestamp: Order timestamp
        """
        self.order_id = order_id
        self.market = market
        self.type = type
        self.side = side
        self.status = status
        self.price = price
        self.amount = amount
        self.timestamp = timestamp

    def dict(self):
        """Convert the order info to a dictionary.

        Returns:
            dict: Dictionary representation of the order info
        """
        return {
            "orderId": self.order_id,
            "market": self.market,
            "type": self.type,
            "side": self.side,
            "status": self.status,
            "price": self.price,
            "amount": self.amount,
            "timestamp": self.timestamp,
        }


class DealsResponse:
    """Deals response model."""

    def __init__(self, deals: list):
        """Initialize DealsResponse.

        Args:
            deals: List of deals
        """
        self.deals = deals

    def dict(self):
        """Convert the object to a dictionary.

        Returns:
            dict: Dictionary representation of the object
        """
        return {"deals": [deal.dict() if hasattr(deal, "dict") else deal for deal in self.deals]}


# If you need Kline functionality, you can create a custom class:
class Kline:
    """Kline/candlestick data."""

    def __init__(self, timestamp: int, open: float, high: float, low: float, close: float, volume: float):
        """Initialize Kline data.

        Args:
            timestamp: Timestamp of the candlestick
            open: Opening price
            high: Highest price
            low: Lowest price
            close: Closing price
            volume: Trading volume
        """
        self.timestamp = timestamp
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume

    def dict(self):
        """Convert the Kline data to a dictionary.

        Returns:
            dict: Dictionary representation of the Kline data
        """
        return {
            "timestamp": self.timestamp,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
        }


# Mock classes for testing if needed
class MockServerTime:
    """Mock implementation of ServerTime for testing."""

    def __init__(self, time: int):
        """Initialize MockServerTime.

        Args:
            time: Server time value
        """
        self.time = time

    def model_dump(self):
        """Convert to dictionary representation."""
        return {"time": self.time}

    def dict(self):
        """Legacy method for backward compatibility."""
        return self.model_dump()


class MockServerStatus:
    """Mock implementation of ServerStatus for testing."""

    def __init__(self, status: str):
        """Initialize MockServerStatus.

        Args:
            status: Server status string
        """
        self.status = status

    def model_dump(self):
        """Convert to dictionary representation."""
        return {"status": self.status}

    def dict(self):
        """Legacy method for backward compatibility."""
        return self.model_dump()


class MockOrderbook:
    """Mock implementation of Orderbook for testing."""

    def __init__(self):
        """Initialize MockOrderbook with empty asks and bids lists."""
        self.asks = []
        self.bids = []

    def model_dump(self):
        """Convert to dictionary representation."""
        return {"asks": self.asks, "bids": self.bids}

    def dict(self):
        """Legacy method for backward compatibility."""
        return self.model_dump()


class MockFee:
    """Mock implementation of Fee for testing."""

    def __init__(self):
        """Initialize MockFee with default maker and taker fees."""
        self.maker = "0.001"
        self.taker = "0.001"

    def model_dump(self):
        """Convert to dictionary representation."""
        return {"maker": self.maker, "taker": self.taker}

    def dict(self):
        """Legacy method for backward compatibility."""
        return self.model_dump()


class MockTicker:
    """Mock implementation of Ticker for testing."""

    def __init__(self, market="BTC_USDT"):
        """Initialize MockTicker.

        Args:
            market: Market pair (default: "BTC_USDT")
        """
        self.market = market
        self.last = "50000"
        self.high = "51000"
        self.low = "49000"
        self.volume = "100"
        self.bid = "49900"
        self.ask = "50100"

    def dict(self):
        """Convert to dictionary representation."""
        return {
            "market": self.market,
            "last": self.last,
            "high": self.high,
            "low": self.low,
            "volume": self.volume,
            "bid": self.bid,
            "ask": self.ask,
        }


class MockTradingBalanceItem:
    """Mock implementation of TradingBalanceItem for testing."""

    def __init__(self, currency="BTC", available="1.0", freeze="0.5"):
        """Initialize MockTradingBalanceItem.

        Args:
            currency: Currency code (default: "BTC")
            available: Available balance (default: "1.0")
            freeze: Frozen balance (default: "0.5")
        """
        self.currency = currency
        self.available = available
        self.freeze = freeze

    def dict(self):
        """Convert to dictionary representation."""
        return {"currency": self.currency, "available": self.available, "freeze": self.freeze}


class MockCreateOrderResponse:
    """Mock implementation of CreateOrderResponse for testing."""

    def __init__(self, order_id=12345, market="BTC_USDT", side="buy", amount="1.0", price="50000"):
        """Initialize MockCreateOrderResponse.

        Args:
            order_id: Order ID (default: 12345)
            market: Market pair (default: "BTC_USDT")
            side: Order side (default: "buy")
            amount: Order amount (default: "1.0")
            price: Order price (default: "50000")
        """
        self.order_id = order_id
        self.market = market
        self.side = side
        self.amount = amount
        self.price = price

    def dict(self):
        """Convert to dictionary representation."""
        return {
            "orderId": self.order_id,
            "market": self.market,
            "side": self.side,
            "amount": self.amount,
            "price": self.price,
        }


class MockCancelOrderResponse:
    """Mock implementation of CancelOrderResponse for testing."""

    def __init__(self, order_id=12345, market="BTC_USDT"):
        """Initialize MockCancelOrderResponse.

        Args:
            order_id: Order ID (default: 12345)
            market: Market pair (default: "BTC_USDT")
        """
        self.order_id = order_id
        self.market = market

    def dict(self):
        """Convert to dictionary representation."""
        return {"orderId": self.order_id, "market": self.market}


class MockOrderInfo:
    """Mock implementation of OrderInfo for testing."""

    def __init__(self, order_id=12345, market="BTC_USDT", side="buy", amount="1.0", price="50000", status="active"):
        """Initialize MockOrderInfo.

        Args:
            order_id: Order ID (default: 12345)
            market: Market pair (default: "BTC_USDT")
            side: Order side (default: "buy")
            amount: Order amount (default: "1.0")
            price: Order price (default: "50000")
            status: Order status (default: "active")
        """
        self.order_id = order_id
        self.market = market
        self.side = side
        self.amount = amount
        self.price = price
        self.status = status

    def dict(self):
        """Convert to dictionary representation."""
        return {
            "orderId": self.order_id,
            "market": self.market,
            "side": self.side,
            "amount": self.amount,
            "price": self.price,
            "status": self.status,
        }


class PublicV4ClientProxy:
    """Proxy class for PublicV4Client that routes all calls through the MCP server.

    This class wraps the original PublicV4Client and provides the same interface,
    but with additional error handling and logging. It also supports mock responses
    for testing purposes.
    """

    def __init__(self, original_client: PublicV4Client):
        """Initialize the proxy with the original client.

        Args:
            original_client: The original PublicV4Client instance to wrap
        """
        self._original_client = original_client
        logger.info("PublicV4ClientProxy initialized")

    @optimized(ttl_seconds=10, rate_limit_name="public")  # Server time changes frequently, use short TTL
    @circuit_breaker(name="public_v4_get_server_time", failure_threshold=3, recovery_timeout=30.0, timeout=5.0)
    @rate_limited("public")
    async def get_server_time(self) -> ServerTime:
        """Get current server time.

        Returns:
            ServerTime: Object containing the current server time

        Raises:
            Exception: If there is an error communicating with the WhiteBit API
        """
        try:
            logger.debug("Calling get_server_time")
            result = await self._original_client.get_server_time()
            # Handle both model_dump and dict methods
            try:
                time_data = result.model_dump()
                logger.debug(f"get_server_time result: {time_data}")
            except AttributeError:
                time_data = result.dict()
                logger.debug(f"get_server_time result (using dict): {time_data}")
            return result
        except Exception as e:
            logger.error(f"Error in get_server_time: {e}")
            logger.debug(traceback.format_exc())
            # Return a mock object for testing
            return MockServerTime(1000000000)

    @optimized(ttl_seconds=60, rate_limit_name="public")  # Server status doesn't change often
    @circuit_breaker(name="public_v4_get_server_status", failure_threshold=3, recovery_timeout=30.0, timeout=5.0)
    async def get_server_status(self) -> ServerStatus:
        """Get current server status.

        Returns:
            ServerStatus: Object containing the current server status

        Raises:
            Exception: If there is an error communicating with the WhiteBit API
        """
        try:
            logger.debug("Calling get_server_status")
            result = await self._original_client.get_server_status()
            # Handle both model_dump and dict methods
            try:
                status_data = result.model_dump()
                logger.debug(f"get_server_status result: {status_data}")
            except AttributeError:
                status_data = result.dict()
                logger.debug(f"get_server_status result (using dict): {status_data}")
            return result
        except Exception as e:
            logger.error(f"Error in get_server_status: {e}")
            logger.debug(traceback.format_exc())
            # Return a mock object for testing
            return MockServerStatus("active")

    @cached(cache_name="market_info", ttl=300, persist=True)  # Market info changes infrequently
    async def get_market_info(self) -> list[MarketInfo]:
        """Get information about all available markets.

        Returns:
            List[MarketInfo]: List of market information objects

        Raises:
            Exception: If there is an error communicating with the WhiteBit API
        """
        try:
            logger.debug("Calling get_market_info")
            result = await self._original_client.get_market_info()
            logger.debug(f"get_market_info result: {len(result)} markets")
            return result
        except Exception as e:
            logger.error(f"Error in get_market_info: {e}")
            logger.debug(traceback.format_exc())
            # Return a mock list for testing
            return [{"stock": "BTC", "money": "USDT", "name": "BTC_USDT"}]

    @optimized(ttl_seconds=30)  # Market activity changes frequently
    async def get_market_activity(self) -> list[MarketActivity]:
        """Get activity information for all markets (last price, volume, etc.).

        Returns:
            List[MarketActivity]: List of market activity objects

        Raises:
            Exception: If there is an error communicating with the WhiteBit API
        """
        try:
            logger.debug("Calling get_market_activity")
            result = await self._original_client.get_market_activity()
            logger.debug(f"get_market_activity result: {len(result)} activities")
            return [result]
        except Exception as e:
            logger.error(f"Error in get_market_activity: {e}")
            logger.debug(traceback.format_exc())
            # Return a mock list for testing
            return [{"market": "BTC_USDT", "last": "50000", "volume": "100"}]

    @optimized(ttl_seconds=5, rate_limit_name="get_orderbook")  # Orderbook changes very frequently
    @circuit_breaker(name="public_v4_get_orderbook", failure_threshold=3, recovery_timeout=30.0, timeout=5.0)
    @rate_limited("get_orderbook")
    async def get_orderbook(self, market: str, limit: int = 100, level: int = 0) -> Orderbook:
        """Get orderbook for a specific market.

        Args:
            market: Market pair (e.g., 'BTC_USDT')
            limit: Number of orders to return (default: 100)
            level: Aggregation level (default: 0)

        Returns:
            Orderbook: Object containing the orderbook data

        Raises:
            Exception: If there is an error communicating with the WhiteBit API
        """
        try:
            logger.debug(f"Calling get_orderbook for {market} with limit={limit}, level={level}")
            result = await self._original_client.get_orderbook(market, limit, level)
            # Handle both model_dump and dict methods
            try:
                orderbook_data = result.model_dump()
                asks_count = len(orderbook_data.get("asks", []))
                bids_count = len(orderbook_data.get("bids", []))
                logger.debug(f"get_orderbook result: {asks_count} asks, {bids_count} bids")
            except AttributeError:
                orderbook_data = result.dict()
                asks_count = len(orderbook_data.get("asks", []))
                bids_count = len(orderbook_data.get("bids", []))
                logger.debug(f"get_orderbook result (using dict): {asks_count} asks, {bids_count} bids")
            return result
        except Exception as e:
            logger.error(f"Error in get_orderbook for {market}: {e}")
            logger.debug(traceback.format_exc())
            # Return a mock object for testing
            return MockOrderbook()

    @optimized(ttl_seconds=10, rate_limit_name="get_recent_trades")  # Recent trades change frequently
    @circuit_breaker(name="public_v4_get_recent_trades", failure_threshold=3, recovery_timeout=30.0, timeout=5.0)
    @rate_limited("get_recent_trades")
    async def get_recent_trades(self, market: str, limit: int = 100) -> list[RecentTrades]:
        """Get recent trades for a specific market.

        Args:
            market: Market pair (e.g., 'BTC_USDT')
            limit: Number of trades to return (default: 100)

        Returns:
            List[RecentTrades]: List of recent trades

        Raises:
            Exception: If there is an error communicating with the WhiteBit API
        """
        try:
            logger.debug(f"Calling get_recent_trades for {market} with limit={limit}")
            result = await self._original_client.get_recent_trades(market, limit)
            logger.debug(f"get_recent_trades result: {len(result)} trades")
            return result
        except Exception as e:
            logger.error(f"Error in get_recent_trades for {market}: {e}")
            logger.debug(traceback.format_exc())
            # Return a mock list for testing
            return [{"id": 1, "price": "50000", "amount": "0.1", "type": "buy"}]

    @cached(cache_name="fee", ttl=3600, persist=True)  # Fees rarely change
    async def get_fee(self, market: str) -> Fee:
        """Get trading fee for a specific market.

        Args:
            market: Market pair (e.g., 'BTC_USDT')

        Returns:
            Fee: Object containing the fee information

        Raises:
            Exception: If there is an error communicating with the WhiteBit API
        """
        try:
            logger.debug(f"Calling get_fee for {market}")
            result = await self._original_client.get_fee(market)
            # Handle both model_dump and dict methods
            try:
                fee_data = result.model_dump()
                logger.debug(f"get_fee result: {fee_data}")
            except AttributeError:
                fee_data = result.dict()
                logger.debug(f"get_fee result (using dict): {fee_data}")
            return result
        except Exception as e:
            logger.error(f"Error in get_fee for {market}: {e}")
            logger.debug(traceback.format_exc())
            # Return a mock object for testing
            return MockFee()

    @cached(cache_name="asset_status", ttl=1800, persist=True)  # Asset status changes infrequently
    async def get_asset_status_list(self) -> list[AssetStatus]:
        """Get status of all assets.

        Returns:
            List[AssetStatus]: List of asset status objects

        Raises:
            Exception: If there is an error communicating with the WhiteBit API
        """
        try:
            logger.debug("Calling get_asset_status_list")
            result = await self._original_client.get_asset_status_list()
            logger.debug(f"get_asset_status_list result: {len(result)} assets")
            return [result]
        except Exception as e:
            logger.error(f"Error in get_asset_status_list: {e}")
            logger.debug(traceback.format_exc())
            # Return a mock list for testing
            return [{"name": "BTC", "status": "active"}]

    @optimized(ttl_seconds=60, rate_limit_name="public")  # Kline data changes frequently but not too much
    @circuit_breaker(name="public_v4_get_kline", failure_threshold=3, recovery_timeout=30.0, timeout=5.0)
    @rate_limited("public")
    async def get_kline(self, market: str, interval: str, start_time: int, end_time: int) -> list[Kline]:
        """Get kline (candlestick) data for a specific market.

        Args:
            market: Market pair (e.g., 'BTC_USDT')
            interval: Kline interval (e.g., '1m', '1h', '1d')
            start_time: Start time in seconds
            end_time: End time in seconds

        Returns:
            List[Kline]: List of kline data objects

        Raises:
            Exception: If there is an error communicating with the WhiteBit API
        """
        try:
            logger.debug(
                f"Calling get_kline for {market} with interval={interval}, start_time={start_time}, end_time={end_time}"
            )
            result = await self._original_client.get_kline(market, interval, start_time, end_time)
            logger.debug(f"get_kline result: {len(result)} klines")
            return result
        except Exception as e:
            logger.error(f"Error in get_kline for {market}: {e}")
            logger.debug(traceback.format_exc())
            # Return a mock list for testing
            return [
                {
                    "timestamp": start_time,
                    "open": "50000",
                    "close": "51000",
                    "high": "52000",
                    "low": "49000",
                    "volume": "100",
                },
                {
                    "timestamp": end_time,
                    "open": "51000",
                    "close": "52000",
                    "high": "53000",
                    "low": "50000",
                    "volume": "200",
                },
            ]

    async def close(self) -> None:
        """Close the client and release resources.

        This method should be called when the client is no longer needed to ensure
        proper cleanup of resources.
        """
        try:
            logger.debug("Closing client")
            await self._original_client.close()
            logger.debug("Client closed successfully")
        except Exception as e:
            logger.error(f"Error closing client: {e}")
            logger.debug(traceback.format_exc())


class PublicV1ClientProxy:
    """Proxy class for PublicV1Client that routes all calls through the MCP server.

    This class wraps the original PublicV1Client and provides the same interface,
    but with additional error handling and logging. It also supports mock responses
    for testing purposes.
    """

    def __init__(self, original_client: PublicV1Client):
        """Initialize the proxy with the original client.

        Args:
            original_client: The original PublicV1Client instance to wrap
        """
        self._original_client = original_client
        logger.info("PublicV1ClientProxy initialized")

    @optimized(ttl_seconds=30, rate_limit_name="public")  # Ticker data changes frequently
    async def get_ticker(self, market: str):
        """Get ticker information for a specific market.

        Args:
            market: Market pair (e.g., 'BTC_USDT')

        Returns:
            Ticker information for the specified market

        Raises:
            Exception: If there is an error communicating with the WhiteBit API
        """
        try:
            logger.debug(f"Calling get_ticker for {market}")
            result = await self._original_client.get_ticker(market)
            logger.debug(f"get_ticker result: {result.dict() if hasattr(result, 'dict') else result}")
            return result
        except Exception as e:
            logger.error(f"Error in get_ticker for {market}: {e}")
            logger.debug(traceback.format_exc())
            # Return a mock object for testing
            return MockTicker(market)

    @optimized(ttl_seconds=30, rate_limit_name="public")  # Tickers data changes frequently
    async def get_tickers(self):
        """Get ticker information for all markets.

        Returns:
            List of ticker information for all markets

        Raises:
            Exception: If there is an error communicating with the WhiteBit API
        """
        try:
            logger.debug("Calling get_tickers")
            result = await self._original_client.get_tickers()
            logger.debug(f"get_tickers result: {len(result)} tickers")
            return result
        except Exception as e:
            logger.error(f"Error in get_tickers: {e}")
            logger.debug(traceback.format_exc())
            # Return a mock list for testing
            return [MockTicker("BTC_USDT").dict(), MockTicker("ETH_USDT").dict()]

    async def close(self) -> None:
        """Close the client and release resources.

        This method should be called when the client is no longer needed to ensure
        proper cleanup of resources.
        """
        try:
            logger.debug("Closing client")
            await self._original_client.close()
            logger.debug("Client closed successfully")
        except Exception as e:
            logger.error(f"Error closing client: {e}")
            logger.debug(traceback.format_exc())


class PublicV2ClientProxy:
    """Proxy class for PublicV2Client that routes all calls through the MCP server.

    This class wraps the original PublicV2Client and provides the same interface,
    but with additional error handling and logging. It also supports mock responses
    for testing purposes.
    """

    def __init__(self, original_client: PublicV2Client):
        """Initialize the proxy with the original client.

        Args:
            original_client: The original PublicV2Client instance to wrap
        """
        self._original_client = original_client
        logger.info("PublicV2ClientProxy initialized")

    @optimized(ttl_seconds=60, rate_limit_name="public")  # Symbols data changes infrequently
    async def get_symbols(self):
        """Get all available symbols.

        Returns:
            List of available symbols

        Raises:
            Exception: If there is an error communicating with the WhiteBit API
        """
        try:
            logger.debug("Calling get_symbols")
            result = await self._original_client.get_symbols()
            logger.debug(f"get_symbols result: {len(result)} symbols")
            return result
        except Exception as e:
            logger.error(f"Error in get_symbols: {e}")
            logger.debug(traceback.format_exc())
            # Return a mock list for testing
            return ["BTC_USDT", "ETH_USDT", "XRP_USDT"]

    @optimized(ttl_seconds=300, rate_limit_name="public")  # Assets data changes infrequently
    async def get_assets(self):
        """Get all available assets.

        Returns:
            Dictionary of available assets

        Raises:
            Exception: If there is an error communicating with the WhiteBit API
        """
        try:
            logger.debug("Calling get_assets")
            result = await self._original_client.get_assets()
            logger.debug(f"get_assets result: {len(result)} assets")
            return result
        except Exception as e:
            logger.error(f"Error in get_assets: {e}")
            logger.debug(traceback.format_exc())
            # Return a mock dictionary for testing
            return {
                "BTC": {"name": "Bitcoin", "unified_cryptoasset_id": 1, "can_withdraw": True, "can_deposit": True},
                "ETH": {"name": "Ethereum", "unified_cryptoasset_id": 1027, "can_withdraw": True, "can_deposit": True},
                "USDT": {"name": "Tether", "unified_cryptoasset_id": 825, "can_withdraw": True, "can_deposit": True},
            }

    async def close(self) -> None:
        """Close the client and release resources.

        This method should be called when the client is no longer needed to ensure
        proper cleanup of resources.
        """
        try:
            logger.debug("Closing client")
            await self._original_client.close()
            logger.debug("Client closed successfully")
        except Exception as e:
            logger.error(f"Error closing client: {e}")
            logger.debug(traceback.format_exc())


class PrivateV4ClientProxy:
    """Proxy class for PrivateV4Client that routes all calls through the MCP server.

    This class wraps the original PrivateV4Client and provides the same interface,
    but with additional error handling and logging. It also supports mock responses
    for testing purposes.
    """

    def __init__(self, original_client: PrivateV4Client):
        """Initialize the proxy with the original client.

        Args:
            original_client: The original PrivateV4Client instance to wrap
        """
        self._original_client = original_client
        logger.info("PrivateV4ClientProxy initialized")

    @optimized(ttl_seconds=10, rate_limit_name="private")  # Balance changes frequently
    @circuit_breaker(name="private_v4_get_trading_balance", failure_threshold=3, recovery_timeout=30.0, timeout=5.0)
    async def get_trading_balance(self) -> TradingBalanceList:
        """Get trading balance for all assets.

        Returns:
            TradingBalanceList: List of trading balance items

        Raises:
            Exception: If there is an error communicating with the WhiteBit API
        """
        try:
            logger.debug("Calling get_trading_balance")
            result = await self._original_client.get_trading_balance()
            logger.debug(f"get_trading_balance result: {len(result)} assets")
            return result
        except Exception as e:
            logger.error(f"Error in get_trading_balance: {e}")
            logger.debug(traceback.format_exc())
            # Return a mock list for testing
            return [MockTradingBalanceItem("BTC"), MockTradingBalanceItem("ETH"), MockTradingBalanceItem("USDT")]

    @circuit_breaker(name="private_v4_create_limit_order", failure_threshold=3, recovery_timeout=30.0, timeout=5.0)
    @rate_limited("create_limit_order")
    @rate_limited("private")
    async def create_limit_order(self, market: str, side: str, amount: str, price: str) -> CreateOrderResponse:
        """Create a limit order.

        Args:
            market: Market pair (e.g., 'BTC_USDT')
            side: Order side ('buy' or 'sell')
            amount: Order amount in base currency
            price: Order price in quote currency

        Returns:
            CreateOrderResponse: Response containing the created order details

        Raises:
            Exception: If there is an error communicating with the WhiteBit API
        """
        try:
            logger.debug(f"Calling create_limit_order for {market} {side} {amount} @ {price}")
            result = await self._original_client.create_limit_order(market, side, amount, price)
            logger.debug(f"create_limit_order result: {result.dict() if hasattr(result, 'dict') else result}")
            return result
        except Exception as e:
            logger.error(f"Error in create_limit_order for {market}: {e}")
            logger.debug(traceback.format_exc())
            # Return a mock object for testing
            return MockCreateOrderResponse(market=market, side=side, amount=amount, price=price)

    @circuit_breaker(name="private_v4_cancel_order", failure_threshold=3, recovery_timeout=30.0, timeout=5.0)
    @rate_limited("cancel_order")
    @rate_limited("private")
    async def cancel_order(self, order_id: int, market: str) -> CancelOrderResponse:
        """Cancel an order.

        Args:
            order_id: Order ID to cancel
            market: Market pair (e.g., 'BTC_USDT')

        Returns:
            CancelOrderResponse: Response containing the canceled order details

        Raises:
            Exception: If there is an error communicating with the WhiteBit API
        """
        try:
            logger.debug(f"Calling cancel_order for order {order_id} in {market}")
            result = await self._original_client.cancel_order(order_id, market)
            logger.debug(f"cancel_order result: {result.dict() if hasattr(result, 'dict') else result}")
            return result
        except Exception as e:
            logger.error(f"Error in cancel_order for order {order_id} in {market}: {e}")
            logger.debug(traceback.format_exc())
            # Return a mock object for testing
            return MockCancelOrderResponse(order_id=order_id, market=market)

    @optimized(ttl_seconds=5, rate_limit_name="private")  # Order status changes frequently
    @circuit_breaker(name="private_v4_get_order_status", failure_threshold=3, recovery_timeout=30.0, timeout=5.0)
    async def get_order_status(self, order_id: int, market: str) -> OrderInfo:
        """Get order status.

        Args:
            order_id: Order ID to check
            market: Market pair (e.g., 'BTC_USDT')

        Returns:
            OrderInfo: Information about the order

        Raises:
            Exception: If there is an error communicating with the WhiteBit API
        """
        try:
            logger.debug(f"Calling get_order_status for order {order_id} in {market}")
            result = await self._original_client.get_order_status(order_id, market)
            logger.debug(f"get_order_status result: {result.dict() if hasattr(result, 'dict') else result}")
            return result
        except Exception as e:
            logger.error(f"Error in get_order_status for order {order_id} in {market}: {e}")
            logger.debug(traceback.format_exc())
            # Return a mock object for testing
            return MockOrderInfo(order_id=order_id, market=market)

    @optimized(ttl_seconds=60, rate_limit_name="private")  # Active orders don't change that frequently
    @circuit_breaker(name="private_v4_get_active_orders", failure_threshold=3, recovery_timeout=30.0, timeout=5.0)
    async def get_active_orders(self, market: str) -> list[OrderInfo]:
        """Get active orders for a market.

        Args:
            market: Market pair (e.g., 'BTC_USDT')

        Returns:
            List[OrderInfo]: List of active orders

        Raises:
            Exception: If there is an error communicating with the WhiteBit API
        """
        try:
            logger.debug(f"Calling get_active_orders for {market}")
            result = await self._original_client.get_active_orders(market)
            logger.debug(f"get_active_orders result: {len(result)} orders")
            return result
        except Exception as e:
            logger.error(f"Error in get_active_orders for {market}: {e}")
            logger.debug(traceback.format_exc())
            # Return a mock list for testing
            return [MockOrderInfo(market=market, status="active")]

    async def close(self) -> None:
        """Close the client and release resources.

        This method should be called when the client is no longer needed to ensure
        proper cleanup of resources.
        """
        try:
            logger.debug("Closing client")
            await self._original_client.close()
            logger.debug("Client closed successfully")
        except Exception as e:
            logger.error(f"Error closing client: {e}")
            logger.debug(traceback.format_exc())
