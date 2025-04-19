"""Example script to demonstrate how to use the WhiteBit MCP client."""

import asyncio
import json
import os

from aiowhitebit_mcp.client import WhiteBitMCPClient

# Set the server URL (could be a local server or a remote one)
os.environ["WHITEBIT_MCP_URL"] = "http://0.0.0.0:8000"  # For SSE transport
# os.environ["WHITEBIT_MCP_URL"] = "ws://localhost:8000/mcp"  # For WebSocket transport
# os.environ["WHITEBIT_MCP_URL"] = "python examples/run_server.py"  # For stdio transport


async def main():
    """Main function to demonstrate client usage"""
    async with WhiteBitMCPClient() as client:
        # Get server time
        server_time = await client.get_server_time()
        print("Server time:", json.dumps(server_time, indent=2))

        # Get market info for BTC_USDT
        btc_usdt_info = await client.get_market_resource("BTC_USDT")
        print("\nBTC_USDT market info:", json.dumps(btc_usdt_info, indent=2))

        # Get recent trades for BTC_USDT
        recent_trades = await client.get_recent_trades("BTC_USDT", limit=5)
        print("\nRecent BTC_USDT trades:", json.dumps(recent_trades, indent=2))

        # Get last price for BTC_USDT using WebSocket
        last_price = await client.get_last_price("BTC_USDT")
        print("\nBTC_USDT last price:", json.dumps(last_price, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
