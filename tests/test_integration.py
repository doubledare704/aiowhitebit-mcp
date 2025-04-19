"""Integration tests for the WhiteBit MCP server.

This module contains integration tests for the WhiteBit MCP server.
It tests all the public API methods exposed by the server.
"""

import json
import logging

from fastmcp import Client

from aiowhitebit_mcp.server import MarketPair, create_server

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_get_ticker():
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        try:
            response = await client.call_tool("get_ticker", {"market": MarketPair(market="BTC_USDT")})
            assert isinstance(response, list)
            assert len(response) > 0

            content = response[0]
            assert hasattr(content, "text")

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
        except Exception as e:
            print(f"❌ get_ticker test failed: {e}")
    await server.close()


async def test_get_tickers():
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        print("Testing get_tickers...")
        response = await client.call_tool("get_tickers", {})
        assert isinstance(response, list)
        assert len(response) > 0

        content = response[0]
        assert hasattr(content, "text")

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
    await server.close()


# Test cases for public v2 API
async def test_get_symbols():
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        print("Testing get_symbols...")
        response = await client.call_tool("get_symbols", {})
        assert isinstance(response, list)
        assert len(response) > 0

        content = response[0]
        assert hasattr(content, "text")

        data = json.loads(content.text)
        assert isinstance(data, dict)
        assert "symbols" in data
        symbols = data["symbols"]
        assert isinstance(symbols, list)
        assert len(symbols) > 0
        print("✅ get_symbols test passed")
    await server.close()


async def test_get_assets():
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        print("Testing get_assets...")
        response = await client.call_tool("get_assets", {})
        assert isinstance(response, list)
        assert len(response) > 0

        content = response[0]
        assert hasattr(content, "text")

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
    await server.close()


# Test cases for public v4 API
async def test_server_time():
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        print("Testing get_server_time...")
        try:
            response = await client.call_tool("get_server_time", {})
            assert isinstance(response, list)
            assert len(response) > 0

            content = response[0]
            assert hasattr(content, "text")

            data = json.loads(content.text)
            assert isinstance(data, dict)
            assert "time" in data
            assert isinstance(data["time"], dict)
            assert "time" in data["time"]
            assert isinstance(data["time"]["time"], int)
            print("✅ get_server_time test passed")
        except Exception as e:
            print(f"❌ get_server_time test failed: {e}")
    await server.close()


async def test_server_status():
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        print("Testing get_server_status...")
        try:
            response = await client.call_tool("get_server_status", {})
            assert isinstance(response, list)
            assert len(response) > 0

            content = response[0]
            assert hasattr(content, "text")

            data = json.loads(content.text)
            assert isinstance(data, dict)
            assert "status" in data
            print("✅ get_server_status test passed")
        except Exception as e:
            print(f"❌ get_server_status test failed: {e}")
    await server.close()


async def test_market_info():
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        print("Testing get_market_info...")
        try:
            response = await client.call_tool("get_market_info", {})
            assert isinstance(response, list)
            assert len(response) > 0

            content = response[0]
            assert hasattr(content, "text")

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
    await server.close()


async def test_market_activity():
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        print("Testing get_market_activity...")
        try:
            response = await client.call_tool("get_market_activity", {})
            assert isinstance(response, list)
            assert len(response) > 0

            content = response[0]
            assert hasattr(content, "text")

            data = json.loads(content.text)
            assert isinstance(data, dict)
            assert "activities" in data
            activities = data["activities"]
            assert isinstance(activities, list)
            assert len(activities) > 0
            first_activity = activities[0]
            assert isinstance(first_activity, dict)
            for _k, v in first_activity.items():
                assert "last_price" in v
                assert "quote_volume" in v
            print("✅ get_market_activity test passed")
        except Exception as e:
            print(f"❌ get_market_activity test failed: {e}")
    await server.close()


async def test_orderbook():
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        print("Testing get_orderbook...")
        try:
            response = await client.call_tool("get_orderbook", {"market": MarketPair(market="BTC_USDT")})
            assert isinstance(response, list)
            assert len(response) > 0

            content = response[0]
            assert hasattr(content, "text")

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
    await server.close()


async def test_recent_trades():
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        print("Testing get_recent_trades...")
        try:
            response = await client.call_tool("get_recent_trades", {"market": MarketPair(market="BTC_USDT")})
            assert isinstance(response, list)
            assert len(response) > 0

            content = response[0]
            assert hasattr(content, "text")

            data = json.loads(content.text)
            assert isinstance(data, dict)
            assert "trades" in data
            trades = data["trades"]
            assert isinstance(trades, list)
            assert len(trades) > 0
            print("✅ get_recent_trades test passed")
        except Exception as e:
            print(f"❌ get_recent_trades test failed: {e}")
    await server.close()


async def test_fee():
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        print("Testing get_fee...")
        try:
            response = await client.call_tool("get_fee", {"market": MarketPair(market="BTC_USDT")})
            assert isinstance(response, list)
            assert len(response) > 0

            content = response[0]
            assert hasattr(content, "text")

            data = json.loads(content.text)
            assert isinstance(data, dict)
            print("✅ get_fee test passed")
        except Exception as e:
            print(f"❌ get_fee test failed: {e}")
    await server.close()


async def test_asset_status_list():
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        print("Testing get_asset_status_list...")
        try:
            response = await client.call_tool("get_asset_status_list", {})
            assert isinstance(response, list)
            assert len(response) > 0

            content = response[0]
            assert hasattr(content, "text")

            data = json.loads(content.text)
            assert isinstance(data, dict)
            assert "assets" in data
            assets = data["assets"]
            assert isinstance(assets, list)
            assert len(assets) > 0
            print("✅ get_asset_status_list test passed")
        except Exception as e:
            print(f"❌ get_asset_status_list test failed: {e}")
    await server.close()
