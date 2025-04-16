"""Tests for the WhiteBit MCP server.
"""

import pytest
from fastmcp import Client

from aiowhitebit_mcp.server import create_server


@pytest.fixture
async def server():
    """Create a WhiteBit MCP server for testing"""
    server = create_server(name="WhiteBit MCP Test")
    yield server
    # Clean up
    await server.close()


@pytest.fixture
async def client(server):
    """Create a client connected to the test server"""
    async with Client(server.mcp) as client:
        yield client


@pytest.mark.asyncio
async def test_server_time(client):
    """Test getting server time"""
    result = await client.call_tool("get_server_time", {})
    assert result.content[0].type == "text"
    data = result.content[0].text
    assert "time" in data


@pytest.mark.asyncio
async def test_market_info(client):
    """Test getting market info"""
    result = await client.call_tool("get_market_info", {})
    assert result.content[0].type == "text"
    data = result.content[0].text
    # Check that we have at least one market
    assert len(data) > 0


@pytest.mark.asyncio
async def test_market_resource(client):
    """Test reading market resource"""
    result = await client.read_resource("whitebit://markets")
    assert result[0].type == "text"
    data = result[0].content
    # Check that we have at least one market
    assert len(data) > 0
