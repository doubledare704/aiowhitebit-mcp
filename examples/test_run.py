"""Simple test script to verify the server works.
"""

import asyncio

from fastmcp import Client

from aiowhitebit_mcp.server import create_server


async def test():
    """Test the server by making a simple request"""
    # Create the server
    server = create_server()

    # Create a client connected to the server
    async with Client(server.mcp) as client:
        # Call the get_server_time tool
        result = await client.call_tool("get_server_time", {})
        print("Server time response:", result)

    # Close the server
    await server.close()


if __name__ == "__main__":
    asyncio.run(test())
