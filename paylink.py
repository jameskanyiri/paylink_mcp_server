# Import FastMCP server framework and necessary modules
from mcp.server.fastmcp import FastMCP
from src.servers.mpesa.utils.auth import get_access_token, refresh_access_token
from src.servers.mpesa.models.context import MPesaContext
from src.servers.mpesa.tools.mpesa_tools import MpesaTools

import time
import asyncio
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

# Define the application lifespan context manager
# This handles setup and teardown logic for the app's lifecycle
@asynccontextmanager
async def app_lifespan(app: FastMCP) -> AsyncIterator[MPesaContext]:
    try:
        # Fetch initial access token from Safaricom API
        token_data = await get_access_token()
        
        # Create and store context containing the token and expiry info
        context = MPesaContext(
            access_token=token_data["access_token"],
            expires_at=time.time() + token_data["expires_in"],
            refresh_task=None,
        )
        
        # Start a background task to refresh the token before it expires
        context.refresh_task = asyncio.create_task(refresh_access_token(context))
        
        # Yield the context to the server for use in tools
        yield context
    finally:
        # On shutdown, cancel the token refresh task gracefully
        if context.refresh_task:
            context.refresh_task.cancel()
            try:
                await context.refresh_task
            except asyncio.CancelledError:
                pass

# Create an instance of the MCP server with a lifespan context
mcp = FastMCP("PayLink MCP server", lifespan=app_lifespan)

# Register M-Pesa tools with the server (like stk_push)
MpesaTools(mcp)

# Entry point to start the MCP server
if __name__ == "__main__":
    mcp.run(transport="stdio")
