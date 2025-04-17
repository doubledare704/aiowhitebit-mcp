import json
import pytest
import pytest_asyncio
from fastmcp import Client

from aiowhitebit_mcp.server import create_server
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(name)s:%(message)s')
log = logging.getLogger(__name__)
# Tell pytest-asyncio to use one event loop for the whole module
pytestmark = pytest.mark.asyncio(scope="module")


@pytest_asyncio.fixture(scope="module")
async def server():
    """Create a WhiteBit MCP server for testing"""
    # Make sure create_server gets the correct loop if needed explicitly,
    # though usually it picks up the running loop automatically.
    _server = create_server(name="WhiteBit MCP Test")
    try:
        yield _server
    finally:
        await _server.close()


@pytest_asyncio.fixture(scope="module")
async def client(server):
    """Create a client connected to the test server"""
    # This client will now be created and connect within the module-scoped event loop
    client = Client(server.mcp)
    await client.__aenter__()
    try:
        yield client
    finally:
        await client.__aexit__(None, None, None)


# # No changes needed in the tests themselves
# @pytest.mark.asyncio
# async def test_server_time(client):
#     """Test getting server time"""
#     response = await client.call_tool("get_server_time", {})
#     assert isinstance(response, list)
#     assert len(response) > 0
#
#     content = response[0]
#     assert hasattr(content, 'text')
#
#     # Parse the JSON string from text
#     data = json.loads(content.text)
#     assert isinstance(data, dict)
#     assert "time" in data
#     assert isinstance(data["time"], dict)
#     assert "time" in data["time"]
#     assert isinstance(data["time"]["time"], int)
@pytest.mark.asyncio
async def test_server_time(client):
    """Test getting server time"""
    log.debug("test_server_time: START")
    try:
        log.debug("test_server_time: Awaiting client.call_tool('get_server_time')...")
        response = await client.call_tool("get_server_time", {})
        # *** If the test hangs, you WON'T see the next log line ***
        log.debug(f"test_server_time: client.call_tool returned: {type(response)}")

        assert isinstance(response, list)
        log.debug("test_server_time: Assertion 1 passed")
        assert len(response) > 0
        log.debug("test_server_time: Assertion 2 passed")

        content = response[0]
        log.debug(f"test_server_time: Got content: {type(content)}")
        assert hasattr(content, 'text')
        log.debug("test_server_time: Assertion 3 passed")

        log.debug(f"test_server_time: Parsing JSON: {getattr(content, 'text', 'N/A')}")
        data = json.loads(content.text)
        log.debug(f"test_server_time: Parsed data: {type(data)}")
        # ... rest of assertions ...
        log.debug("test_server_time: All assertions passed")

    except Exception as e:
        log.exception("test_server_time: EXCEPTION occurred") # Logs traceback
        raise
    finally:
        log.debug("test_server_time: END")

@pytest.mark.asyncio
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


@pytest.mark.asyncio
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