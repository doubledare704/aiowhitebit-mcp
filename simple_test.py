"""Simple test script to verify our implementation.
"""

import asyncio
import json
from aiowhitebit_mcp.proxy import PublicV4ClientProxy, MockServerTime
from aiowhitebit.clients.public import PublicV4Client

async def test_proxy():
    """Test the proxy implementation"""
    # Create a mock server time
    mock_time = MockServerTime(1000000000)
    print(f"Mock server time: {mock_time.model_dump()}")
    
    # Create the original client and wrap it with our proxy
    original_client = PublicV4Client()
    proxy_client = PublicV4ClientProxy(original_client)
    
    # Test get_server_time
    print("Testing get_server_time...")
    result = await proxy_client.get_server_time()
    print(f"Server time result: {result.model_dump()}")
    
    # Close the client
    await original_client.close()
    await proxy_client.close()

if __name__ == "__main__":
    asyncio.run(test_proxy())
