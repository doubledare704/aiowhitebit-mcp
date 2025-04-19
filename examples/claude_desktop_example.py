"""Example script to run the WhiteBit MCP server for Claude Desktop."""

import os

from aiowhitebit_mcp.server import create_server

# Create the server with a descriptive name
server = create_server(
    name="WhiteBit Crypto Exchange",
    api_key=os.environ.get("WHITEBIT_API_KEY"),
    api_secret=os.environ.get("WHITEBIT_API_SECRET"),
)

# Run the server with stdio transport (for Claude Desktop)
if __name__ == "__main__":
    server.run(transport="stdio")
