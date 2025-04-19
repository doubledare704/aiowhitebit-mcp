"""Test script for the private API methods.

This script tests the private API methods exposed by the WhiteBit MCP server.
"""

import json
import logging

from fastmcp import Client

from aiowhitebit_mcp.server import MarketPair, OrderParams, create_server

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_get_trading_balance():
    """Test getting trading balance."""
    print("Testing get_trading_balance...")
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        try:
            response = await client.call_tool("get_trading_balance", {})
            assert isinstance(response, list)
            assert len(response) > 0

            content = response[0]
            assert hasattr(content, "text")

            data = json.loads(content.text)
            assert isinstance(data, dict)
            assert "balance" in data
            balance = data["balance"]
            assert isinstance(balance, list)
            assert len(balance) > 0
            first_balance = balance[0]
            assert isinstance(first_balance, dict)
            assert "currency" in first_balance
            assert "available" in first_balance
            assert "freeze" in first_balance
            print("✅ get_trading_balance test passed")
        except Exception as e:
            print(f"❌ get_trading_balance test failed: {e}")
        finally:
            await server.close()


async def test_create_limit_order():
    """Test creating a limit order."""
    print("Testing create_limit_order...")
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        try:
            order_params = OrderParams(market="BTC_USDT", side="buy", amount=1.0, price=50000.0)
            response = await client.call_tool("create_limit_order", {"order": order_params})
            assert isinstance(response, list)
            assert len(response) > 0

            content = response[0]
            assert hasattr(content, "text")

            data = json.loads(content.text)
            assert isinstance(data, dict)
            assert "order" in data
            order = data["order"]
            assert isinstance(order, dict)
            assert "orderId" in order
            assert "market" in order
            assert "side" in order
            assert "amount" in order
            assert "price" in order
            print("✅ create_limit_order test passed")
        except Exception as e:
            print(f"❌ create_limit_order test failed: {e}")
        finally:
            await server.close()


async def test_cancel_order():
    """Test canceling an order."""
    print("Testing cancel_order...")
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        try:
            response = await client.call_tool(
                "cancel_order", {"order_id": 12345, "market": MarketPair(market="BTC_USDT")}
            )
            assert isinstance(response, list)
            assert len(response) > 0

            content = response[0]
            assert hasattr(content, "text")

            data = json.loads(content.text)
            assert isinstance(data, dict)
            assert "order" in data
            order = data["order"]
            assert isinstance(order, dict)
            assert "orderId" in order
            assert "market" in order
            print("✅ cancel_order test passed")
        except Exception as e:
            print(f"❌ cancel_order test failed: {e}")
        finally:
            await server.close()


async def test_get_order_status():
    """Test getting order status."""
    print("Testing get_order_status...")
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        try:
            response = await client.call_tool(
                "get_order_status", {"order_id": 12345, "market": MarketPair(market="BTC_USDT")}
            )
            assert isinstance(response, list)
            assert len(response) > 0

            content = response[0]
            assert hasattr(content, "text")

            data = json.loads(content.text)
            assert isinstance(data, dict)
            assert "order" in data
            order = data["order"]
            assert isinstance(order, dict)
            assert "orderId" in order
            assert "market" in order
            assert "side" in order
            assert "amount" in order
            assert "price" in order
            assert "status" in order
            print("✅ get_order_status test passed")
        except Exception as e:
            print(f"❌ get_order_status test failed: {e}")
        finally:
            await server.close()


async def test_get_active_orders():
    """Test getting active orders."""
    print("Testing get_active_orders...")
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        try:
            response = await client.call_tool("get_active_orders", {"market": MarketPair(market="BTC_USDT")})
            assert isinstance(response, list)
            assert len(response) > 0

            content = response[0]
            assert hasattr(content, "text")

            data = json.loads(content.text)
            assert isinstance(data, dict)
            assert "orders" in data
            orders = data["orders"]
            assert isinstance(orders, list)
            assert len(orders) > 0
            first_order = orders[0]
            assert isinstance(first_order, dict)
            assert "orderId" in first_order
            assert "market" in first_order
            assert "status" in first_order
            print("✅ get_active_orders test passed")
        except Exception as e:
            print(f"❌ get_active_orders test failed: {e}")
        finally:
            await server.close()
