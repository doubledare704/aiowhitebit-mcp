"""Example script demonstrating basic WhiteBit MCP client usage."""

import asyncio
import json
import logging
from datetime import datetime

from aiowhitebit_mcp.client import WhiteBitMCPClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Demonstrate basic client functionality."""
    async with WhiteBitMCPClient() as client:
        # Basic market data
        logger.info("Getting server time...")
        server_time = await client.get_server_time()
        print(f"Server time: {datetime.fromtimestamp(server_time['time']['time'])}\n")

        # Market information
        market = "BTC_USDT"
        logger.info(f"Getting market info for {market}...")
        market_info = await client.get_market_resource(market)
        print(f"{market} Market Info:", json.dumps(market_info, indent=2), "\n")

        # Real-time price via WebSocket
        logger.info(f"Getting real-time price for {market}...")
        price = await client.get_last_price(market)
        print(f"Current {market} price:", json.dumps(price, indent=2), "\n")

        # Order book
        logger.info(f"Getting order book for {market}...")
        orderbook = await client.get_orderbook(market)
        print(f"{market} Order Book (top 5):")
        print("Asks:", json.dumps(orderbook["orderbook"]["asks"][:5], indent=2))
        print("Bids:", json.dumps(orderbook["orderbook"]["bids"][:5], indent=2), "\n")

        # Recent trades
        logger.info(f"Getting recent trades for {market}...")
        trades = await client.get_recent_trades(market, limit=5)
        print(f"Recent {market} trades:", json.dumps(trades, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
