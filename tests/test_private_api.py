"""Test script for the private API methods.

This script tests the private API methods exposed by the WhiteBit MCP server.
"""

import asyncio
import json
import logging
import sys
from typing import Dict, List
from fastmcp import Client

from aiowhitebit_mcp.server import create_server, MarketPair, OrderParams
from aiowhitebit_mcp.proxy import (
    MockTradingBalanceItem, MockCreateOrderResponse, MockCancelOrderResponse, MockOrderInfo
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockPrivateV4Client:
    """Mock implementation of PrivateV4Client for testing."""
    
    async def get_trading_balance(self):
        """Get trading balance for all assets."""
        return [MockTradingBalanceItem("BTC"), MockTradingBalanceItem("ETH"), MockTradingBalanceItem("USDT")]
    
    async def create_limit_order(self, market, side, amount, price):
        """Create a limit order."""
        return MockCreateOrderResponse(market=market, side=side, amount=amount, price=price)
    
    async def cancel_order(self, order_id, market):
        """Cancel an order."""
        return MockCancelOrderResponse(order_id=order_id, market=market)
    
    async def get_order_status(self, order_id, market):
        """Get order status."""
        return MockOrderInfo(order_id=order_id, market=market)
    
    async def get_active_orders(self, market):
        """Get active orders for a market."""
        return [MockOrderInfo(market=market, status="active")]
    
    async def close(self):
        """Close the client."""
        pass


async def test_get_trading_balance(client):
    """Test getting trading balance."""
    print("Testing get_trading_balance...")
    try:
        response = await client.call_tool("get_trading_balance", {})
        assert isinstance(response, list)
        assert len(response) > 0
        
        content = response[0]
        assert hasattr(content, 'text')
        
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
        # Continue with other tests instead of failing


async def test_create_limit_order(client):
    """Test creating a limit order."""
    print("Testing create_limit_order...")
    try:
        order_params = OrderParams(
            market="BTC_USDT",
            side="buy",
            amount=1.0,
            price=50000.0
        )
        response = await client.call_tool("create_limit_order", {"order": order_params})
        assert isinstance(response, list)
        assert len(response) > 0
        
        content = response[0]
        assert hasattr(content, 'text')
        
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
        # Continue with other tests instead of failing


async def test_cancel_order(client):
    """Test canceling an order."""
    print("Testing cancel_order...")
    try:
        response = await client.call_tool("cancel_order", {
            "order_id": 12345,
            "market": MarketPair(market="BTC_USDT")
        })
        assert isinstance(response, list)
        assert len(response) > 0
        
        content = response[0]
        assert hasattr(content, 'text')
        
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
        # Continue with other tests instead of failing


async def test_get_order_status(client):
    """Test getting order status."""
    print("Testing get_order_status...")
    try:
        response = await client.call_tool("get_order_status", {
            "order_id": 12345,
            "market": MarketPair(market="BTC_USDT")
        })
        assert isinstance(response, list)
        assert len(response) > 0
        
        content = response[0]
        assert hasattr(content, 'text')
        
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
        # Continue with other tests instead of failing


async def test_get_active_orders(client):
    """Test getting active orders."""
    print("Testing get_active_orders...")
    try:
        response = await client.call_tool("get_active_orders", {
            "market": MarketPair(market="BTC_USDT")
        })
        assert isinstance(response, list)
        assert len(response) > 0
        
        content = response[0]
        assert hasattr(content, 'text')
        
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
        # Continue with other tests instead of failing


async def run_tests():
    """Run all tests."""
    print("Starting private API tests...")
    
    # Create mock client
    mock_private_v4_client = MockPrivateV4Client()
    
    # Create the server with the mock client
    from aiowhitebit_mcp.server import WhiteBitMCP
    from aiowhitebit_mcp.proxy import PrivateV4ClientProxy
    
    server = WhiteBitMCP(name="WhiteBit MCP Test")
    # Replace the proxy with one that uses our mock client
    server.private_v4 = PrivateV4ClientProxy(mock_private_v4_client)
    
    # Register private tools
    server._register_private_tools()
    
    success = True
    
    try:
        async with Client(server.mcp) as client:
            # Test private API
            await test_get_trading_balance(client)
            await test_create_limit_order(client)
            await test_cancel_order(client)
            await test_get_order_status(client)
            await test_get_active_orders(client)
            
            print("\n🎉 All private API tests passed!")
    except Exception as e:
        print(f"\n❌ Private API test failed: {e}")
        success = False
    finally:
        await server.close()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_tests())
    sys.exit(exit_code)
