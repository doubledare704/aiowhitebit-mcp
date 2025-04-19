"""Test configuration and fixtures for the aiowhitebit-mcp package."""

import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from fastmcp import Client

from aiowhitebit_mcp.server import create_server


@pytest_asyncio.fixture
async def server():
    """Create a WhiteBit MCP server for testing."""
    _server = create_server(name="WhiteBit MCP Test")
    yield _server
    await _server.close()


@pytest_asyncio.fixture
async def client(server) -> AsyncGenerator[Client, None]:
    """Create a client connected to the test server."""
    async with Client(server.mcp) as client:
        yield client


@pytest_asyncio.fixture
async def authenticated_server():
    """Create a WhiteBit MCP server with test API credentials."""
    _server = create_server(
        name="WhiteBit MCP Test",
        api_key=os.getenv("TEST_API_KEY", "test_key"),
        api_secret=os.getenv("TEST_API_SECRET", "test_secret"),
    )
    yield _server
    await _server.close()


@pytest_asyncio.fixture
async def authenticated_client(authenticated_server) -> AsyncGenerator[Client, None]:
    """Create an authenticated client connected to the test server."""
    async with Client(authenticated_server.mcp) as client:
        yield client


@pytest.fixture
def market_pair() -> str:
    """Return a test market pair."""
    return "BTC_USDT"


@pytest.fixture
def mock_api_response():
    """Return a mock API response factory."""

    def _create_response(data=None, error=None):
        return {
            "success": error is None,
            "data": data or {},
            "error": error,
        }

    return _create_response
