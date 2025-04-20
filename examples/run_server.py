"""Example script to run the WhiteBit MCP server."""


from aiowhitebit_mcp.server import create_server

# Create the server
server = create_server(
    name="WhiteBit MCP Example"
)

# Run the server with stdio transport (for use with Claude Desktop)
if __name__ == "__main__":
    server.run(transport="stdio")
