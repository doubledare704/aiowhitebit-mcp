import pytest_asyncio
from fastmcp import Client
from aiowhitebit_mcp.server import create_server


@pytest_asyncio.fixture
async def server():
    """Create a WhiteBit MCP server for testing"""
    _server = create_server(name="WhiteBit MCP Test")
    yield _server
    await _server.close()


@pytest_asyncio.fixture
async def client(server):
    """Create a client connected to the test server"""
    async with Client(server.mcp) as client:
        yield client
