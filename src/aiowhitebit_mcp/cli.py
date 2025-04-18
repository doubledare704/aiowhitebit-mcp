"""Command-line interface for running the WhiteBit MCP server.
"""

import argparse
import os

from .server import create_server


def main():
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(description="WhiteBit MCP Server")

    parser.add_argument(
        "--name",
        type=str,
        default="WhiteBit MCP",
        help="Name of the MCP server"
    )

    parser.add_argument(
        "--api-key",
        type=str,
        default=os.environ.get("WHITEBIT_API_KEY"),
        help="WhiteBit API key (can also be set via WHITEBIT_API_KEY environment variable)"
    )

    parser.add_argument(
        "--api-secret",
        type=str,
        default=os.environ.get("WHITEBIT_API_SECRET"),
        help="WhiteBit API secret (can also be set via WHITEBIT_API_SECRET environment variable)"
    )

    parser.add_argument(
        "--transport",
        type=str,
        choices=["stdio", "sse", "ws"],
        default="stdio",
        help="Transport protocol to use (stdio, sse, or ws)"
    )

    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind to when using sse or ws transport"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to when using sse or ws transport"
    )

    args = parser.parse_args()

    # Create and run the server
    server = create_server(
        name=args.name,
        api_key=args.api_key,
        api_secret=args.api_secret
    )

    # Run with the specified transport
    if args.transport == "stdio":
        server.run(transport="stdio")
    elif args.transport == "sse":
        server.run(transport="sse", host=args.host, port=args.port)
    elif args.transport == "ws":
        server.run(transport="ws", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
