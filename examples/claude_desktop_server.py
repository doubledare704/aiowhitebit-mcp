"""Example script to run the WhiteBit MCP server for Claude Desktop."""

from aiowhitebit_mcp.server import create_server
import asyncio
# Create the server with a descriptive name
server = create_server(
    name="WhiteBit Crypto Exchange"
)

# Run the server with stdio transport (for Claude Desktop)
if __name__ == "__main__":
    asyncio.run(
    server.run(transport="stdio")
    )
