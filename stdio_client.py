from typing import Optional
from mcp import ClientSession, StdioServerParameters
from contextlib import AsyncExitStack
from mcp.client.stdio import stdio_client
import asyncio
import nest_asyncio

# Apply nest_asyncio to allow nested event loops (helpful in notebooks or some runtime environments)
nest_asyncio.apply()

class MCPClient:
    def __init__(self) -> None:
        # Initialize the client session and an async exit stack for resource management
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        
    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server using the provided server script path.

        Args:
            server_script_path (str): Path to the MCP server script to run.
        """
        # Define parameters to launch the server using stdio communication
        server_params = StdioServerParameters(
            command="python",            # Launch the server with Python
            args=[server_script_path],   # Pass the server script path as an argument
            env=None                     # No special environment variables needed
        )

        # Create a stdio transport connection to the server and enter its context
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport

        # Establish a client session with the MCP server using stdio transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        # Initialize the session (typically performs a handshake or setup)
        await self.session.initialize()
        
        # List available tools exposed by the server
        response = await self.session.list_tools()
        tools = response.tools
        
        return tools
    
    async def cleanup(self):
        """Clean up all resources by closing the async exit stack."""
        await self.exit_stack.aclose()
    
    
async def main():
    # Instantiate the MCP client
    client = MCPClient()
    
    try:
        # Connect to the MCP server script and fetch available tools
        tools = await client.connect_to_server("paylink.py")

        # Print out the list of tools
        for tool in tools:
            print(tool)

    finally:
        # Ensure cleanup is always performed, even if an error occurs
        await client.cleanup()
        

if __name__ == "__main__":
    # Run the main coroutine using asyncio's event loop
    asyncio.run(main())
