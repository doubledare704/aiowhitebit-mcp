"""Tests for the WhiteBit MCP server's public v4 client wrapper.

This module contains tests for all the wrapped calls to the public v4 client.
"""

import json
import logging

from fastmcp import Client

from aiowhitebit_mcp.server import MarketPair, create_server

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_server_time():
    """Test getting server time."""
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
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
        finally:
            await server.close()


async def test_server_status():
    """Test getting server status."""
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        try:
            response = await client.call_tool("get_server_status", {})
            assert isinstance(response, list)
            assert len(response) > 0

            content = response[0]
            assert hasattr(content, "text")

            data = json.loads(content.text)
            assert isinstance(data, dict)
            assert "status" in data
            assert isinstance(data["status"], dict)
        finally:
            await server.close()


async def test_market_info():
    """Test getting market info."""
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
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
            assert "name" in first_market
        finally:
            await server.close()


async def test_market_activity():
    """Test getting market activity."""
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
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
        finally:
            await server.close()


async def test_orderbook():
    """Test getting orderbook."""
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
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
            assert isinstance(orderbook["asks"], list)
            assert isinstance(orderbook["bids"], list)
        finally:
            await server.close()


async def test_recent_trades():
    """Test getting recent trades."""
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
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
            first_trade = trades[0]
            assert isinstance(first_trade, dict)
            assert "id" in first_trade
            assert "price" in first_trade
            assert "amount" in first_trade
            assert "type" in first_trade
        finally:
            await server.close()


async def test_fee():
    """Test getting fee."""
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        try:
            response = await client.call_tool("get_fee", {"market": MarketPair(market="BTC_USDT")})
            assert isinstance(response, list)
            assert len(response) > 0

            content = response[0]
            assert hasattr(content, "text")

            data = json.loads(content.text)
            assert isinstance(data, dict)
            assert "fee" in data
            fee = data["fee"]
            assert isinstance(fee, dict)
            assert "maker" in fee
            assert "taker" in fee
        finally:
            await server.close()


async def test_asset_status_list():
    """Test getting asset status list."""
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
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
            asset_dict = assets[0]
            assert isinstance(asset_dict, dict)
            for _k, v in asset_dict.items():
                assert "name" in v
        finally:
            await server.close()


async def test_market_resource():
    """Test reading market resource."""
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        try:
            response = await client.read_resource("whitebit://markets")
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
        finally:
            await server.close()
