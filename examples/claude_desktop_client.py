"""Example script demonstrating WhiteBit MCP client with stdio transport for Claude Desktop."""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime

from aiowhitebit_mcp.client import WhiteBitMCPClient
from fastmcp.client import Client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Demonstrate client functionality with Claude Desktop stdio server."""
    logger.info("Connecting to Claude Desktop stdio server...")
    
    try:
        # Create a client directly with stdio transport
        # Instead of using the environment variable, create the client directly
        client = WhiteBitMCPClient("stdio://")
        
        async with client:
            # Basic market data
            logger.info("Getting server time...")
            server_time = await client.get_server_time()
            print(f"Server time: {datetime.fromtimestamp(server_time['time']['time'])}\n")

            # Market information
            market = "BTC_USDT"
            logger.info(f"Getting market info for {market}...")
            market_info = await client.get_market_resource(market)
            print(f"{market} Market Info:", json.dumps(market_info, indent=2), "\n")

            # Get health status
            logger.info("Getting server health status...")
            health = await client.client.call("health")
            print(f"Server health status:", json.dumps(health, indent=2), "\n")
            
            # Get metrics
            logger.info("Getting server metrics...")
            metrics = await client.client.call("metrics")
            print(f"Server metrics:", json.dumps(metrics, indent=2), "\n")
            
    except Exception as e:
        logger.error(f"Error connecting to Claude Desktop stdio server: {e}")
        print("\nMake sure the server is running with stdio transport.")
        print("You can start the server with:")
        print("  - python -m examples.claude_desktop_server")
        print("  - Or: aiowhitebit-mcp --transport stdio")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())