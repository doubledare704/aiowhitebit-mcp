import pytest
import pytest_asyncio
from fastmcp import Client

from aiowhitebit_mcp.server import create_server

# Tell pytest-asyncio to use function-scoped event loops
pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def server():
    """Create a WhiteBit MCP server for testing"""
    _server = create_server(name="WhiteBit MCP Test")
    yield _server
    await _server.close()


@pytest_asyncio.fixture
async def client(server):
    """Create a client connected to the test server"""
    client = Client(server.mcp)
    await client.__aenter__()
    yield client
    await client.__aexit__(None, None, None)