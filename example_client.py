import asyncio
import os
from aiowhitebit_mcp.client import WhiteBitMCPClient

async def check_server():
    # Try to connect to the MCP server
    # You can specify the server URL directly or set the WHITEBIT_MCP_URL environment variable
    server_url = os.environ.get("WHITEBIT_MCP_URL", "http://localhost:8000")
    
    print(f"Connecting to MCP server at {server_url}...")
    
    try:
        async with WhiteBitMCPClient(server_url=server_url) as client:
            # Check server health
            health = await client.call("health")
            print(f"Server health: {health}")
            
            # Get metrics
            metrics = await client.call("metrics")
            print(f"Server metrics: {metrics}")
            
            # Try some WhiteBit API calls
            try:
                server_time = await client.get_server_time()
                print(f"Server time: {server_time}")
                
                markets = await client.get_market_info()
                print(f"Available markets: {len(markets)} markets")
            except Exception as e:
                print(f"Error calling WhiteBit API: {e}")
    
    except ConnectionError as e:
        print(f"Failed to connect to MCP server: {e}")
        print("\nMake sure the server is running with the correct transport.")
        print("You can start the server with:")
        print("  - For WebSocket: aiowhitebit-mcp --transport ws --host localhost --port 8000")
        print("  - For SSE: aiowhitebit-mcp --transport sse --host localhost --port 8000")

if __name__ == "__main__":
    asyncio.run(check_server())