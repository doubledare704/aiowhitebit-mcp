"""Example script to run the WhiteBit MCP server with SSE transport.
"""

import os

from aiowhitebit_mcp.server import create_server

# Create the server
server = create_server(
    name="WhiteBit API Server",
    api_key=os.environ.get("WHITEBIT_API_KEY"),
    api_secret=os.environ.get("WHITEBIT_API_SECRET")
)

# Run the server with SSE transport
if __name__ == "__main__":
    server.run(transport="sse", host="127.0.0.1", port=8000)
