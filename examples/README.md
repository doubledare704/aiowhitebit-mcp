# WhiteBit MCP Examples

This directory contains example scripts for using the WhiteBit MCP server and client.

## Server Examples

- `sse_server.py`: Run the WhiteBit MCP server with SSE transport
- `websocket_server.py`: Run the WhiteBit MCP server with WebSocket transport
- `claude_desktop_server.py`: Run the WhiteBit MCP server with stdio transport for Claude Desktop

## Client Examples

- `sse_client.py`: Connect to a WhiteBit MCP server using SSE transport
- `websocket_client.py`: Connect to a WhiteBit MCP server using WebSocket transport
- `advanced_client.py`: Advanced client usage with various API calls

## Running the Examples

1. Start a server:
   ```
   python -m examples.sse_server
   ```

2. In another terminal, run a client:
   ```
   python -m examples.sse_client
   ```

For Claude Desktop integration, run:
```
python -m examples.claude_desktop_server
```

## Command-line Interface

You can also use the command-line interface:

```
# Run with SSE transport
aiowhitebit-mcp --transport sse --host localhost --port 8000

# Run with WebSocket transport
aiowhitebit-mcp --transport ws --host localhost --port 8000

# Run with stdio transport (for Claude Desktop)
aiowhitebit-mcp --transport stdio
```
