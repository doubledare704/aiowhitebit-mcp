#!/usr/bin/env python
"""Run the multi-exchange MCP server with the web interface.

This script runs the multi-exchange MCP server with the web interface enabled.
"""

import argparse
import asyncio
import logging
import os
import signal
import sys

from aiowhitebit_mcp.exchange import ExchangeType
from aiowhitebit_mcp.multi_exchange_server import create_server

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def run_server(args):
    """Run the multi-exchange MCP server.
    
    Args:
        args: Command-line arguments
    """
    # Set up exchanges
    exchanges = {}
    
    # Add WhiteBit exchange if credentials are provided
    if args.whitebit_api_key and args.whitebit_api_secret:
        exchanges[ExchangeType.WHITEBIT] = {
            "api_key": args.whitebit_api_key,
            "api_secret": args.whitebit_api_secret
        }
    
    # Add Binance exchange if credentials are provided
    if args.binance_api_key and args.binance_api_secret:
        exchanges[ExchangeType.BINANCE] = {
            "api_key": args.binance_api_key,
            "api_secret": args.binance_api_secret
        }
    
    # Create the server
    server = create_server(
        name=args.name,
        exchanges=exchanges,
        default_exchange=args.default_exchange,
        web_interface=True,
        web_host=args.host,
        web_port=args.port
    )
    
    # Set up signal handlers
    loop = asyncio.get_event_loop()
    
    def signal_handler():
        logger.info("Received signal, shutting down...")
        loop.create_task(server.close())
    
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)
    
    # Run forever
    try:
        logger.info(f"Multi-exchange MCP server running")
        logger.info(f"Web interface available at http://{args.host}:{args.port}")
        
        # Keep the server running
        while True:
            await asyncio.sleep(1)
    finally:
        await server.close()


def parse_args():
    """Parse command-line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Run the multi-exchange MCP server")
    
    parser.add_argument(
        "--name",
        default="Multi-Exchange MCP",
        help="Name of the MCP server"
    )
    
    parser.add_argument(
        "--default-exchange",
        type=ExchangeType,
        default=ExchangeType.WHITEBIT,
        help="Default exchange to use when no exchange is specified"
    )
    
    parser.add_argument(
        "--whitebit-api-key",
        default=os.environ.get("WHITEBIT_API_KEY"),
        help="WhiteBit API key (can also be set with WHITEBIT_API_KEY environment variable)"
    )
    
    parser.add_argument(
        "--whitebit-api-secret",
        default=os.environ.get("WHITEBIT_API_SECRET"),
        help="WhiteBit API secret (can also be set with WHITEBIT_API_SECRET environment variable)"
    )
    
    parser.add_argument(
        "--binance-api-key",
        default=os.environ.get("BINANCE_API_KEY"),
        help="Binance API key (can also be set with BINANCE_API_KEY environment variable)"
    )
    
    parser.add_argument(
        "--binance-api-secret",
        default=os.environ.get("BINANCE_API_SECRET"),
        help="Binance API secret (can also be set with BINANCE_API_SECRET environment variable)"
    )
    
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host to bind the web interface to"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to bind the web interface to"
    )
    
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(run_server(args))
    sys.exit(0)
