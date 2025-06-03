import os
import time
import asyncio
import json
import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse, Response

from src.servers.mpesa.utils.auth import get_access_token, refresh_access_token
from src.servers.mpesa.models.context import MPesaContext
from src.servers.mpesa.tools.mpesa_tools import MpesaTools


logger = logging.getLogger(__name__)

# Load env
load_dotenv(override=True)


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
mcp = FastMCP(
    "PayLink_MCP_server",
    host="0.0.0.0",  # Only used for SSE transport (localhost)
    port=8050,  # Only used for SSE transport (set this to any port)
    lifespan=app_lifespan,
    stateless_http=True
)

@mcp.custom_route("/mpesa/callback", methods=["POST"])
async def mpesa_callback_handler(request: Request) -> Response:
    """Handle M-Pesa webhook callback."""
    try:
        # Read the request body (asynchronous)
        body = await request.body()
        logger.info(f"Received M-Pesa webhook: {body}")

        # Parse the JSON payload (M-Pesa sends JSON data)
        payload = json.loads(body.decode("utf-8"))
        
        # Process the M-Pesa payload (add your logic here)
        # Example: Log the transaction details
        logger.info(f"M-Pesa Payload: {payload}")

        # Return a 200 OK response to acknowledge receipt
        return Response(status_code=200, content="Webhook received successfully")
    
    except Exception as e:
        # Log the error for debugging
        logger.error(f"Unexpected error: {e}")
        # Return a 500 error response to M-Pesa
        return Response(status_code=500, content=f"Error processing webhook: {str(e)}")

MpesaTools(mcp=mcp)

# Entry point to start the MCP server
if __name__ == "__main__":

    mcp.run(transport="streamable-http")
