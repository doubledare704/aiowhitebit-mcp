"""Tests for the WhiteBit MCP server's public v4 client wrapper.

This module contains tests for all the wrapped calls to the public v4 client.
"""

import json

from aiowhitebit_mcp.server import MarketPair


async def test_server_time(client):
    """Test getting server time"""
    response = await client.call_tool("get_server_time", {})
    assert isinstance(response, list)
    assert len(response) > 0

    content = response[0]
    assert hasattr(content, 'text')

    # Parse the JSON string from text
    data = json.loads(content.text)
    assert isinstance(data, dict)
    assert "time" in data
    assert isinstance(data["time"], dict)
    assert "time" in data["time"]
    assert isinstance(data["time"]["time"], int)


async def test_server_status(client):
    """Test getting server status"""
    response = await client.call_tool("get_server_status", {})
    assert isinstance(response, list)
    assert len(response) > 0

    content = response[0]
    assert hasattr(content, 'text')

    # Parse the JSON string from text
    data = json.loads(content.text)
    assert isinstance(data, dict)
    assert "status" in data
    assert isinstance(data["status"], dict)


async def test_market_info(client):
    """Test getting market info"""
    response = await client.call_tool("get_market_info", {})
    assert isinstance(response, list)
    assert len(response) > 0

    content = response[0]
    assert hasattr(content, 'text')

    # Parse the JSON string from text
    data = json.loads(content.text)
    assert isinstance(data, dict)
    assert "markets" in data
    markets = data["markets"]
    assert isinstance(markets, list)
    # Check that we have at least one market
    assert len(markets) > 0
    # Check first market has required fields
    first_market = markets[0]
    assert isinstance(first_market, dict)
    assert "stock" in first_market
    assert "money" in first_market
    assert "name" in first_market


async def test_market_activity(client):
    """Test getting market activity"""
    response = await client.call_tool("get_market_activity", {})
    assert isinstance(response, list)
    assert len(response) > 0

    content = response[0]
    assert hasattr(content, 'text')

    # Parse the JSON string from text
    data = json.loads(content.text)
    assert isinstance(data, dict)
    assert "activities" in data
    activities = data["activities"]
    assert isinstance(activities, list)
    # Check that we have at least one activity
    assert len(activities) > 0
    # Check first activity has required fields
    first_activity = activities[0]
    assert isinstance(first_activity, dict)
    assert "market" in first_activity
    assert "last" in first_activity
    assert "volume" in first_activity


async def test_orderbook(client):
    """Test getting orderbook"""
    # Create a proper MarketPair instance
    response = await client.call_tool("get_orderbook", {"market": MarketPair(market="BTC_USDT")})
    assert isinstance(response, list)
    assert len(response) > 0

    content = response[0]
    assert hasattr(content, 'text')

    # Parse the JSON string from text
    data = json.loads(content.text)
    assert isinstance(data, dict)
    assert "orderbook" in data
    orderbook = data["orderbook"]
    assert isinstance(orderbook, dict)
    assert "asks" in orderbook
    assert "bids" in orderbook
    assert isinstance(orderbook["asks"], list)
    assert isinstance(orderbook["bids"], list)


async def test_recent_trades(client):
    """Test getting recent trades"""
    # Create a proper MarketPair instance
    response = await client.call_tool("get_recent_trades", {"market": MarketPair(market="BTC_USDT")})
    assert isinstance(response, list)
    assert len(response) > 0

    content = response[0]
    assert hasattr(content, 'text')

    # Parse the JSON string from text
    data = json.loads(content.text)
    assert isinstance(data, dict)
    assert "trades" in data
    trades = data["trades"]
    assert isinstance(trades, list)
    # Check that we have at least one trade
    assert len(trades) > 0
    # Check first trade has required fields
    first_trade = trades[0]
    assert isinstance(first_trade, dict)
    assert "id" in first_trade
    assert "price" in first_trade
    assert "amount" in first_trade
    assert "type" in first_trade


async def test_fee(client):
    """Test getting fee"""
    # Create a proper MarketPair instance
    response = await client.call_tool("get_fee", {"market": MarketPair(market="BTC_USDT")})
    assert isinstance(response, list)
    assert len(response) > 0

    content = response[0]
    assert hasattr(content, 'text')

    # Parse the JSON string from text
    data = json.loads(content.text)
    assert isinstance(data, dict)
    assert "fee" in data
    fee = data["fee"]
    assert isinstance(fee, dict)
    assert "maker" in fee
    assert "taker" in fee


async def test_asset_status_list(client):
    """Test getting asset status list"""
    response = await client.call_tool("get_asset_status_list", {})
    assert isinstance(response, list)
    assert len(response) > 0

    content = response[0]
    assert hasattr(content, 'text')

    # Parse the JSON string from text
    data = json.loads(content.text)
    assert isinstance(data, dict)
    assert "assets" in data
    assets = data["assets"]
    assert isinstance(assets, list)
    # Check that we have at least one asset
    assert len(assets) > 0
    # Check first asset has required fields
    first_asset = assets[0]
    assert isinstance(first_asset, dict)
    assert "name" in first_asset
    assert "status" in first_asset


async def test_market_resource(client):
    """Test reading market resource"""
    response = await client.read_resource("whitebit://markets")
    assert isinstance(response, list)
    assert len(response) > 0

    content = response[0]
    assert hasattr(content, 'text')

    # Parse the JSON string from text
    data = json.loads(content.text)
    assert isinstance(data, dict)
    assert "markets" in data
    markets = data["markets"]
    assert isinstance(markets, list)
    # Check that we have at least one market
    assert len(markets) > 0
    # Check first market has required fields
    first_market = markets[0]
    assert isinstance(first_market, dict)
    assert "stock" in first_market
    assert "money" in first_market
