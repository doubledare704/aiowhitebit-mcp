"""Simple test script to verify our implementation.
"""

import asyncio
import json
from fastmcp import Client
from src.aiowhitebit_mcp.server import create_server


async def test_server_time():
    """Test getting server time"""
    # Create the server
    server = create_server()
    
    # Create a client connected to the server
    client = Client(server.mcp)
    await client.__aenter__()
    
    try:
        # Call the get_server_time tool
        print("Calling get_server_time...")
        response = await client.call_tool("get_server_time", {})
        print(f"Response type: {type(response)}")
        
        if isinstance(response, list) and len(response) > 0:
            content = response[0]
            print(f"Content type: {type(content)}")
            
            if hasattr(content, 'text'):
                print(f"Content text: {content.text}")
                
                # Parse the JSON string from text
                data = json.loads(content.text)
                print(f"Parsed data: {data}")
                
                # Check the structure
                if isinstance(data, dict) and "time" in data:
                    print("✅ Test passed: Response has 'time' key")
                    if isinstance(data["time"], dict) and "time" in data["time"]:
                        print("✅ Test passed: Response has 'time.time' key")
                        if isinstance(data["time"]["time"], int):
                            print("✅ Test passed: 'time.time' is an integer")
                        else:
                            print("❌ Test failed: 'time.time' is not an integer")
                    else:
                        print("❌ Test failed: Response does not have 'time.time' key")
                else:
                    print("❌ Test failed: Response does not have 'time' key")
            else:
                print("❌ Test failed: Content does not have 'text' attribute")
        else:
            print("❌ Test failed: Response is not a list or is empty")
    
    finally:
        # Close the client and server
        await client.__aexit__(None, None, None)
        await server.close()


async def test_market_info():
    """Test getting market info"""
    # Create the server
    server = create_server()
    
    # Create a client connected to the server
    client = Client(server.mcp)
    await client.__aenter__()
    
    try:
        # Call the get_market_info tool
        print("\nCalling get_market_info...")
        response = await client.call_tool("get_market_info", {})
        print(f"Response type: {type(response)}")
        
        if isinstance(response, list) and len(response) > 0:
            content = response[0]
            print(f"Content type: {type(content)}")
            
            if hasattr(content, 'text'):
                print(f"Content text: {content.text}")
                
                # Parse the JSON string from text
                data = json.loads(content.text)
                print(f"Parsed data: {data}")
                
                # Check the structure
                if isinstance(data, dict) and "markets" in data:
                    print("✅ Test passed: Response has 'markets' key")
                    markets = data["markets"]
                    if isinstance(markets, list) and len(markets) > 0:
                        print("✅ Test passed: 'markets' is a non-empty list")
                        first_market = markets[0]
                        if isinstance(first_market, dict) and "stock" in first_market and "money" in first_market:
                            print("✅ Test passed: First market has 'stock' and 'money' keys")
                        else:
                            print("❌ Test failed: First market does not have required fields")
                    else:
                        print("❌ Test failed: 'markets' is not a list or is empty")
                else:
                    print("❌ Test failed: Response does not have 'markets' key")
            else:
                print("❌ Test failed: Content does not have 'text' attribute")
        else:
            print("❌ Test failed: Response is not a list or is empty")
    
    finally:
        # Close the client and server
        await client.__aexit__(None, None, None)
        await server.close()


async def main():
    """Run all tests"""
    await test_server_time()
    await test_market_info()


if __name__ == "__main__":
    asyncio.run(main())
