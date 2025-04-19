import json
import logging

import pytest
from fastmcp import Client

from aiowhitebit_mcp.server import create_server

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s:%(name)s:%(message)s")
log = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_server_time():
    """Test getting server time"""
    log.debug("test_server_time: START")
    server = create_server(name="WhiteBit MCP Test")
    try:
        async with Client(server.mcp) as client:
            log.debug("test_server_time: Awaiting client.call_tool('get_server_time')...")
            response = await client.call_tool("get_server_time", {})
            log.debug(f"test_server_time: client.call_tool returned: {type(response)}")

            assert isinstance(response, list)
            log.debug("test_server_time: Assertion 1 passed")
            assert len(response) > 0
            log.debug("test_server_time: Assertion 2 passed")

            content = response[0]
            log.debug(f"test_server_time: Got content: {type(content)}")
            assert hasattr(content, "text")
            log.debug("test_server_time: Assertion 3 passed")

            log.debug(f"test_server_time: Parsing JSON: {getattr(content, 'text', 'N/A')}")
            data = json.loads(content.text)
            log.debug(f"test_server_time: Parsed data: {type(data)}")

            assert isinstance(data, dict)
            log.debug("test_server_time: Assertion 4 passed")
            assert "time" in data
            log.debug("test_server_time: Assertion 5 passed")
            assert isinstance(data["time"], dict)
            log.debug("test_server_time: Assertion 6 passed")
            assert "time" in data["time"]
            log.debug("test_server_time: Assertion 7 passed")
            assert isinstance(data["time"]["time"], int)
            log.debug("test_server_time: All assertions passed")

    except Exception:
        log.exception("test_server_time: EXCEPTION occurred")  # Logs traceback
        raise
    finally:
        log.debug("test_server_time: END")
        await server.close()


@pytest.mark.asyncio
async def test_market_info():
    """Test getting market info"""
    server = create_server(name="WhiteBit MCP Test")
    try:
        async with Client(server.mcp) as client:
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
    finally:
        await server.close()


@pytest.mark.asyncio
async def test_market_resource():
    """Test reading market resource"""
    server = create_server(name="WhiteBit MCP Test")
    try:
        async with Client(server.mcp) as client:
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
