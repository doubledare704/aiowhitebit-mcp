"""Simple test runner for the WhiteBit MCP server.

This script runs tests for the WhiteBit MCP server without using pytest-asyncio,
which can cause issues with event loops and task management.
"""

import asyncio
import json
import sys
import logging
from fastmcp import Client

from aiowhitebit_mcp.server import create_server, MarketPair
from aiowhitebit_mcp.proxy import MockServerTime, MockServerStatus, MockOrderbook, MockFee

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_server_time(client):
    """Test getting server time"""
    print("Testing get_server_time...")
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


async def test_server_status(client):
    """Test getting server status"""
    print("Testing get_server_status...")
    response = await client.call_tool("get_server_status", {})
    assert isinstance(response, list)
    assert len(response) > 0

    content = response[0]
    assert hasattr(content, 'text')

    data = json.loads(content.text)
    assert isinstance(data, dict)
    assert "status" in data
    print("✅ get_server_status test passed")


async def test_market_info(client):
    """Test getting market info"""
    print("Testing get_market_info...")
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


async def test_market_activity(client):
    """Test getting market activity"""
    print("Testing get_market_activity...")
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


async def test_orderbook(client):
    """Test getting orderbook"""
    print("Testing get_orderbook...")
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


async def test_recent_trades(client):
    """Test getting recent trades"""
    print("Testing get_recent_trades...")
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


async def test_fee(client):
    """Test getting fee"""
    print("Testing get_fee...")
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


async def test_asset_status_list(client):
    """Test getting asset status list"""
    print("Testing get_asset_status_list...")
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


async def run_tests():
    """Run all tests"""
    print("Starting tests...")
    server = create_server(name="WhiteBit MCP Test")

    try:
        async with Client(server.mcp) as client:
            await test_server_time(client)
            await test_server_status(client)
            await test_market_info(client)
            await test_market_activity(client)
            await test_orderbook(client)
            await test_recent_trades(client)
            await test_fee(client)
            await test_asset_status_list(client)

            print("\n🎉 All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    finally:
        await server.close()

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(run_tests())
    sys.exit(exit_code)
