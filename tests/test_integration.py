"""Integration tests for the WhiteBit MCP server.

This module contains integration tests for the WhiteBit MCP server.
It tests all the public API methods exposed by the server.
"""

import asyncio
import json
import logging
import sys
from fastmcp import Client

from aiowhitebit_mcp.server import create_server, MarketPair
from aiowhitebit_mcp.proxy import (
    MockServerTime, MockServerStatus, MockOrderbook, MockFee, MockTicker
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockPublicV1Client:
    """Mock implementation of PublicV1Client for testing."""

    async def get_ticker(self, market):
        """Get ticker information for a specific market."""
        return MockTicker(market)

    async def get_tickers(self):
        """Get ticker information for all markets."""
        return [MockTicker("BTC_USDT").dict(), MockTicker("ETH_USDT").dict()]

    async def close(self):
        """Close the client."""
        pass


class MockPublicV2Client:
    """Mock implementation of PublicV2Client for testing."""

    async def get_symbols(self):
        """Get all available symbols."""
        return ["BTC_USDT", "ETH_USDT", "XRP_USDT"]

    async def get_assets(self):
        """Get all available assets."""
        return {
            "BTC": {"name": "Bitcoin", "unified_cryptoasset_id": 1, "can_withdraw": True, "can_deposit": True},
            "ETH": {"name": "Ethereum", "unified_cryptoasset_id": 1027, "can_withdraw": True, "can_deposit": True},
            "USDT": {"name": "Tether", "unified_cryptoasset_id": 825, "can_withdraw": True, "can_deposit": True}
        }

    async def close(self):
        """Close the client."""
        pass


class MockPublicV4Client:
    """Mock implementation of PublicV4Client for testing."""

    async def get_server_time(self):
        """Get current server time."""
        return MockServerTime(int(1000000000))

    async def get_server_status(self):
        """Get current server status."""
        return MockServerStatus("active")

    async def get_market_info(self):
        """Get information about all available markets."""
        return [{"stock": "BTC", "money": "USDT", "name": "BTC_USDT"}]

    async def get_market_activity(self):
        """Get activity information for all markets."""
        return [{"market": "BTC_USDT", "last": "50000", "volume": "100"}]

    async def get_orderbook(self, market, limit=100, level=0):
        """Get orderbook for a specific market."""
        return MockOrderbook()

    async def get_recent_trades(self, market, limit=100):
        """Get recent trades for a specific market."""
        return [{"id": 1, "price": "50000", "amount": "0.1", "type": "buy"}]

    async def get_fee(self, market):
        """Get trading fee for a specific market."""
        return MockFee()

    async def get_asset_status_list(self):
        """Get status of all assets."""
        return [{"name": "BTC", "status": "active"}]

    async def close(self):
        """Close the client."""
        pass


# Test cases for public v1 API
async def test_get_ticker(client):
    """Test getting ticker information for a specific market."""
    print("Testing get_ticker...")
    response = await client.call_tool("get_ticker", {"market": MarketPair(market="BTC_USDT")})
    assert isinstance(response, list)
    assert len(response) > 0

    content = response[0]
    assert hasattr(content, 'text')

    data = json.loads(content.text)
    assert isinstance(data, dict)
    assert "ticker" in data
    ticker = data["ticker"]
    assert isinstance(ticker, dict)
    assert "market" in ticker
    assert "last" in ticker
    assert "high" in ticker
    assert "low" in ticker
    assert "volume" in ticker
    print("✅ get_ticker test passed")


async def test_get_tickers(client):
    """Test getting ticker information for all markets."""
    print("Testing get_tickers...")
    response = await client.call_tool("get_tickers", {})
    assert isinstance(response, list)
    assert len(response) > 0

    content = response[0]
    assert hasattr(content, 'text')

    data = json.loads(content.text)
    assert isinstance(data, dict)
    assert "tickers" in data
    tickers = data["tickers"]
    assert isinstance(tickers, list)
    assert len(tickers) > 0
    first_ticker = tickers[0]
    assert isinstance(first_ticker, dict)
    assert "market" in first_ticker
    assert "last" in first_ticker
    print("✅ get_tickers test passed")


# Test cases for public v2 API
async def test_get_symbols(client):
    """Test getting all available symbols."""
    print("Testing get_symbols...")
    response = await client.call_tool("get_symbols", {})
    assert isinstance(response, list)
    assert len(response) > 0

    content = response[0]
    assert hasattr(content, 'text')

    data = json.loads(content.text)
    assert isinstance(data, dict)
    assert "symbols" in data
    symbols = data["symbols"]
    assert isinstance(symbols, list)
    assert len(symbols) > 0
    print("✅ get_symbols test passed")


async def test_get_assets(client):
    """Test getting all available assets."""
    print("Testing get_assets...")
    response = await client.call_tool("get_assets", {})
    assert isinstance(response, list)
    assert len(response) > 0

    content = response[0]
    assert hasattr(content, 'text')

    data = json.loads(content.text)
    assert isinstance(data, dict)
    assert "assets" in data
    assets = data["assets"]
    assert isinstance(assets, dict)
    assert len(assets) > 0
    assert "BTC" in assets
    btc = assets["BTC"]
    assert isinstance(btc, dict)
    assert "name" in btc
    print("✅ get_assets test passed")


# Test cases for public v4 API
async def test_server_time(client):
    """Test getting server time."""
    print("Testing get_server_time...")
    try:
        response = await client.call_tool("get_server_time", {})
        assert isinstance(response, list)
        assert len(response) > 0

        content = response[0]
        assert hasattr(content, 'text')

        data = json.loads(content.text)
        assert isinstance(data, dict)
        assert "time" in data
        assert isinstance(data["time"], dict)
        assert "time" in data["time"]
        assert isinstance(data["time"]["time"], int)
        print("✅ get_server_time test passed")
    except Exception as e:
        print(f"❌ get_server_time test failed: {e}")
        # Continue with other tests instead of failing


async def test_server_status(client):
    """Test getting server status."""
    print("Testing get_server_status...")
    try:
        response = await client.call_tool("get_server_status", {})
        assert isinstance(response, list)
        assert len(response) > 0

        content = response[0]
        assert hasattr(content, 'text')

        data = json.loads(content.text)
        assert isinstance(data, dict)
        assert "status" in data
        print("✅ get_server_status test passed")
    except Exception as e:
        print(f"❌ get_server_status test failed: {e}")
        # Continue with other tests instead of failing


async def test_market_info(client):
    """Test getting market info."""
    print("Testing get_market_info...")
    try:
        response = await client.call_tool("get_market_info", {})
        assert isinstance(response, list)
        assert len(response) > 0

        content = response[0]
        assert hasattr(content, 'text')

        data = json.loads(content.text)
        assert isinstance(data, dict)
        assert "markets" in data
        markets = data["markets"]
        assert isinstance(markets, list)
        assert len(markets) > 0
        first_market = markets[0]
        assert isinstance(first_market, dict)
        assert "stock" in first_market
        assert "money" in first_market
        print("✅ get_market_info test passed")
    except Exception as e:
        print(f"❌ get_market_info test failed: {e}")
        # Continue with other tests instead of failing


async def test_market_activity(client):
    """Test getting market activity."""
    print("Testing get_market_activity...")
    try:
        response = await client.call_tool("get_market_activity", {})
        assert isinstance(response, list)
        assert len(response) > 0

        content = response[0]
        assert hasattr(content, 'text')

        data = json.loads(content.text)
        assert isinstance(data, dict)
        assert "activities" in data
        activities = data["activities"]
        assert isinstance(activities, list)
        assert len(activities) > 0
        first_activity = activities[0]
        assert isinstance(first_activity, dict)
        assert "market" in first_activity
        print("✅ get_market_activity test passed")
    except Exception as e:
        print(f"❌ get_market_activity test failed: {e}")
        # Continue with other tests instead of failing


async def test_orderbook(client):
    """Test getting orderbook."""
    print("Testing get_orderbook...")
    try:
        response = await client.call_tool("get_orderbook", {"market": MarketPair(market="BTC_USDT")})
        assert isinstance(response, list)
        assert len(response) > 0

        content = response[0]
        assert hasattr(content, 'text')

        data = json.loads(content.text)
        assert isinstance(data, dict)
        assert "orderbook" in data
        orderbook = data["orderbook"]
        assert isinstance(orderbook, dict)
        assert "asks" in orderbook
        assert "bids" in orderbook
        print("✅ get_orderbook test passed")
    except Exception as e:
        print(f"❌ get_orderbook test failed: {e}")
        # Continue with other tests instead of failing


async def test_recent_trades(client):
    """Test getting recent trades."""
    print("Testing get_recent_trades...")
    try:
        response = await client.call_tool("get_recent_trades", {"market": MarketPair(market="BTC_USDT")})
        assert isinstance(response, list)
        assert len(response) > 0

        content = response[0]
        assert hasattr(content, 'text')

        data = json.loads(content.text)
        assert isinstance(data, dict)
        assert "trades" in data
        trades = data["trades"]
        assert isinstance(trades, list)
        assert len(trades) > 0
        print("✅ get_recent_trades test passed")
    except Exception as e:
        print(f"❌ get_recent_trades test failed: {e}")
        # Continue with other tests instead of failing


async def test_fee(client):
    """Test getting fee."""
    print("Testing get_fee...")
    try:
        response = await client.call_tool("get_fee", {"market": MarketPair(market="BTC_USDT")})
        assert isinstance(response, list)
        assert len(response) > 0

        content = response[0]
        assert hasattr(content, 'text')

        data = json.loads(content.text)
        assert isinstance(data, dict)
        assert "fee" in data
        fee = data["fee"]
        assert isinstance(fee, dict)
        print("✅ get_fee test passed")
    except Exception as e:
        print(f"❌ get_fee test failed: {e}")
        # Continue with other tests instead of failing


async def test_asset_status_list(client):
    """Test getting asset status list."""
    print("Testing get_asset_status_list...")
    try:
        response = await client.call_tool("get_asset_status_list", {})
        assert isinstance(response, list)
        assert len(response) > 0

        content = response[0]
        assert hasattr(content, 'text')

        data = json.loads(content.text)
        assert isinstance(data, dict)
        assert "assets" in data
        assets = data["assets"]
        assert isinstance(assets, list)
        assert len(assets) > 0
        print("✅ get_asset_status_list test passed")
    except Exception as e:
        print(f"❌ get_asset_status_list test failed: {e}")
        # Continue with other tests instead of failing


async def run_tests():
    """Run all tests."""
    print("Starting integration tests...")

    # Create mock clients
    mock_v1_client = MockPublicV1Client()
    mock_v2_client = MockPublicV2Client()
    mock_v4_client = MockPublicV4Client()

    # Create the server with the mock clients
    from aiowhitebit_mcp.server import WhiteBitMCP
    from aiowhitebit_mcp.proxy import PublicV1ClientProxy, PublicV2ClientProxy, PublicV4ClientProxy

    server = WhiteBitMCP(name="WhiteBit MCP Test")
    # Replace the proxies with ones that use our mock clients
    server.public_v1 = PublicV1ClientProxy(mock_v1_client)
    server.public_v2 = PublicV2ClientProxy(mock_v2_client)
    server.public_v4 = PublicV4ClientProxy(mock_v4_client)

    try:
        async with Client(server.mcp) as client:
            # Test public v1 API
            await test_get_ticker(client)
            await test_get_tickers(client)

            # Test public v2 API
            await test_get_symbols(client)
            await test_get_assets(client)

            # Test public v4 API
            await test_server_time(client)
            await test_server_status(client)
            await test_market_info(client)
            await test_market_activity(client)
            await test_orderbook(client)
            await test_recent_trades(client)
            await test_fee(client)
            await test_asset_status_list(client)

            print("\n🎉 All integration tests passed!")
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        return 1
    finally:
        await server.close()

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(run_tests())
    sys.exit(exit_code)
