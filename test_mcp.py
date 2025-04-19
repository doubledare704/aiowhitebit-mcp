"""Simple test script to verify the MCP server implementation."""

import asyncio
import json

from fastmcp import Client

from src.aiowhitebit_mcp.server import create_server


async def test_server_this():
    """Test the server by making a simple request."""
    # Create the server
    server = create_server()
    assert True
    # Create a client connected to the server
    async with Client(server.mcp) as client:
        # Call the get_server_time tool
        print("Calling get_server_time...")
        result = await client.call_tool("get_server_time", {})
        with open("test_output.txt", "w") as f:
            f.write(f"Server time response: {result}\n")
            if result and len(result) > 0:
                f.write(f"Content: {result[0].text}\n")
                try:
                    data = json.loads(result[0].text)
                    f.write(f"Parsed data: {json.dumps(data, indent=2)}\n")
                except Exception as e:
                    f.write(f"Error parsing JSON: {e}\n")

        # Call the get_market_info tool
        print("\nCalling get_market_info...")
        result = await client.call_tool("get_market_info", {})
        with open("test_output.txt", "a") as f:
            f.write(f"\nMarket info response: {result}\n")
            if result and len(result) > 0:
                f.write(f"Content: {result[0].text}\n")
                try:
                    data = json.loads(result[0].text)
                    f.write(f"Parsed data: {json.dumps(data, indent=2)}\n")
                except Exception as e:
                    f.write(f"Error parsing JSON: {e}\n")

    # Close the server
    await server.close()


if __name__ == "__main__":
    asyncio.run(test_server_this())
