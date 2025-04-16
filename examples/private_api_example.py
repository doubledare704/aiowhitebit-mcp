"""Example script to demonstrate how to use the private API endpoints.
"""

import asyncio
import json
import os

from aiowhitebit_mcp.client import WhiteBitMCPClient

# Set the server URL
os.environ["WHITEBIT_MCP_URL"] = "http://localhost:8000/mcp"  # For SSE transport


async def main():
    """Main function to demonstrate private API usage"""
    # Make sure you have set your API credentials in the server
    async with WhiteBitMCPClient() as client:
        # Get trading balance
        balance = await client.get_trading_balance()
        print("Trading balance:", json.dumps(balance, indent=2))

        # Get active orders for BTC_USDT
        active_orders = await client.active_orders("BTC_USDT")
        print("\nActive BTC_USDT orders:", json.dumps(active_orders, indent=2))

        # Example of creating a limit order (commented out for safety)
        """
        order_result = await client.create_limit_order(
            market="BTC_USDT",
            side="buy",
            amount=0.001,  # 0.001 BTC
            price=20000.0  # $20,000 per BTC
        )
        print("\nLimit order result:", json.dumps(order_result, indent=2))
        """


if __name__ == "__main__":
    asyncio.run(main())
