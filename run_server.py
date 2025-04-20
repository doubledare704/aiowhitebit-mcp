#!/usr/bin/env python
"""Run the WhiteBit MCP server with the web interface.

This script runs the WhiteBit MCP server with the web interface enabled.
"""

import argparse
import asyncio
import logging
import signal
import sys

from aiowhitebit_mcp.server import create_server

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def run_server(args):
    """Run the WhiteBit MCP server.

    Args:
        args: Command-line arguments
    """
    # Create the server
    server = create_server(
        name=args.name,
        web_interface=True,
        web_host=args.host,
        web_port=args.port,
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
        logger.info("WhiteBit MCP server running")
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
    parser = argparse.ArgumentParser(description="Run the WhiteBit MCP server")

    parser.add_argument("--name", default="WhiteBit MCP", help="Name of the MCP server")

    parser.add_argument("--host", default="localhost", help="Host to bind the web interface to")

    parser.add_argument("--port", type=int, default=8080, help="Port to bind the web interface to")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(run_server(args))
    sys.exit(0)
