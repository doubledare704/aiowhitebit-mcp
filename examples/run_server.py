"""Example script to run the WhiteBit MCP server.
"""

import os

from aiowhitebit_mcp.server import create_server

# Optional: Set API credentials as environment variables
# os.environ["WHITEBIT_API_KEY"] = "your_api_key"
# os.environ["WHITEBIT_API_SECRET"] = "your_api_secret"

# Create the server
server = create_server(
    name="WhiteBit MCP Example",
    api_key=os.environ.get("WHITEBIT_API_KEY"),
    api_secret=os.environ.get("WHITEBIT_API_SECRET")
)

# Run the server with stdio transport (for use with Claude Desktop)
if __name__ == "__main__":
    server.run(transport="stdio")
