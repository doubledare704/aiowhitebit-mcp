"""Example script demonstrating WebSocket functionality."""

import asyncio
import json
import logging

from aiowhitebit_mcp.client import WhiteBitMCPClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def monitor_market(client: WhiteBitMCPClient, market: str, duration: int = 30):
    """Monitor market price and depth for specified duration."""
    end_time = asyncio.get_event_loop().time() + duration

    while asyncio.get_event_loop().time() < end_time:
        # Get real-time price
        price = await client.get_last_price(market)
        print(f"\n{market} Current Price:", json.dumps(price, indent=2))

        # Get market depth
        depth = await client.get_market_depth(market)
        print(f"\n{market} Market Depth:")
        print("Top 3 Asks:", json.dumps(depth["asks"][:3], indent=2))
        print("Top 3 Bids:", json.dumps(depth["bids"][:3], indent=2))

        await asyncio.sleep(5)  # Wait 5 seconds before next update

async def main():
    """Run WebSocket example."""
    async with WhiteBitMCPClient() as client:
        markets = ["BTC_USDT", "ETH_USDT"]

        for market in markets:
            logger.info(f"Monitoring {market} for 30 seconds...")
            await monitor_market(client, market)

if __name__ == "__main__":
    asyncio.run(main())
