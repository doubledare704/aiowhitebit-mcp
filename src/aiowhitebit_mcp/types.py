"""Type definitions for the aiowhitebit-mcp package."""

from typing import Literal, Optional, Protocol

TransportType = Literal["stdio", "sse", "ws"]


class WhiteBitMCPProtocol(Protocol):
    """Protocol defining the WhiteBitMCP interface."""

    def run(
        self,
        transport: TransportType = "stdio",
        host: Optional[str] = None,
        port: Optional[int] = None,
    ) -> None:
        """Run the MCP server.

        Args:
            transport: Transport type to use
            host: Host to bind to (for network transports)
            port: Port to bind to (for network transports)
        """
        ...
