"""Example script to demonstrate how to use the WebSocket tools."""

import asyncio
import json
import os

from aiowhitebit_mcp.client import WhiteBitMCPClient

# Set the server URL
os.environ["WHITEBIT_MCP_URL"] = "http://localhost:8000/mcp"  # For SSE transport


async def main():
    """Main function to demonstrate WebSocket client usage"""
    async with WhiteBitMCPClient() as client:
        # Get last price for BTC_USDT using WebSocket
        last_price = await client.get_last_price("BTC_USDT")
        print("BTC_USDT last price:", json.dumps(last_price, indent=2))

        # Get market depth for BTC_USDT using WebSocket
        market_depth = await client.get_market_depth("BTC_USDT")
        print("\nBTC_USDT market depth:", json.dumps(market_depth, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
