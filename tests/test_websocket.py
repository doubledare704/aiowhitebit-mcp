"""Tests for the WhiteBit MCP server's WebSocket functionality.

This module contains tests for all the WebSocket-related tools including
the new BookTicker functionality introduced in aiowhitebit 0.3.0.
"""

import json
import logging
from typing import TYPE_CHECKING

from fastmcp.client import Client

from aiowhitebit_mcp.server import MarketPair, create_server

if TYPE_CHECKING:
    from mcp.types import CallToolResult

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_connect_websocket():
    """Test connecting to WebSocket."""
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        try:
            response: CallToolResult = await client.call_tool("connect_websocket", {})
            content = response.content[0]
            assert hasattr(content, "text")

            data = json.loads(content.text)
            assert isinstance(data, dict)
            assert "status" in data
            assert data["status"] == "connected"
        finally:
            await server.close()


async def test_disconnect_websocket():
    """Test disconnecting from WebSocket."""
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        try:
            # First connect
            await client.call_tool("connect_websocket", {})

            # Then disconnect
            response: CallToolResult = await client.call_tool("disconnect_websocket", {})
            content = response.content[0]
            assert hasattr(content, "text")

            data = json.loads(content.text)
            assert isinstance(data, dict)
            assert "status" in data
            assert data["status"] == "disconnected"
        finally:
            await server.close()


async def test_bookticker_subscribe():
    """Test subscribing to BookTicker stream."""
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        try:
            response: CallToolResult = await client.call_tool(
                "bookticker_subscribe", {"market": MarketPair(market="BTC_USDT")}
            )
            content = response.content[0]
            assert hasattr(content, "text")

            data = json.loads(content.text)
            assert isinstance(data, dict)
            assert "subscription" in data
            subscription = data["subscription"]
            assert isinstance(subscription, dict)
            # The exact structure depends on the WebSocket response format
        finally:
            await server.close()


async def test_bookticker_unsubscribe():
    """Test unsubscribing from BookTicker stream."""
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        try:
            # First subscribe
            await client.call_tool("bookticker_subscribe", {"market": MarketPair(market="BTC_USDT")})

            # Then unsubscribe
            response: CallToolResult = await client.call_tool(
                "bookticker_unsubscribe", {"market": MarketPair(market="BTC_USDT")}
            )
            content = response.content[0]
            assert hasattr(content, "text")

            data = json.loads(content.text)
            assert isinstance(data, dict)
            # The unsubscription might return either "unsubscription" or "status" depending on the response
            assert "unsubscription" in data or "status" in data
            # The exact structure depends on the WebSocket response format
        finally:
            await server.close()


async def test_bookticker_unsubscribe_without_connection():
    """Test unsubscribing from BookTicker stream without connection."""
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        try:
            # Try to unsubscribe without connecting first
            response: CallToolResult = await client.call_tool(
                "bookticker_unsubscribe", {"market": MarketPair(market="BTC_USDT")}
            )
            content = response.content[0]
            assert hasattr(content, "text")

            data = json.loads(content.text)
            assert isinstance(data, dict)
            assert "status" in data
            assert data["status"] == "not_connected"
        finally:
            await server.close()
