import asyncio

from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport

server_script = "claude_desktop_server.py" # Assumes this file exists and runs mcp.run()

# Option 1: Inferred transport
client_inferred = Client(server_script)

# Option 2: Explicit transport (e.g., to use a specific python executable or add args)
transport_explicit = PythonStdioTransport(
    script_path=server_script,
    python_cmd="/usr/bin/python3.11", # Specify python version
    # args=["--some-server-arg"], # Pass args to the script
    # env={"MY_VAR": "value"},   # Set environment variables
    # cwd="/path/to/run/in"       # Set working directory
)
client_explicit = Client(transport_explicit)

async def use_stdio_client(client):
    async with client:
        tools = await client.list_tools()
        print(f"Connected via Python Stdio, found tools: {tools}")

if __name__ == "__main__":
    asyncio.run(use_stdio_client(client_inferred))
    # asyncio.run(use_stdio_client(client_explicit))