from typing import Optional
from mcp import ClientSession, StdioServerParameters
from contextlib import AsyncExitStack
from mcp.client.stdio import stdio_client
import asyncio
import nest_asyncio

nest_asyncio.apply()

class MCPClient:
    def __init__(self) -> None:
        #Initialize session and client
        self.session : Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        
    async def connect_to_server(self, server_script_path: str ):
        """Connect to an MCP server

        Args:
            server_script_path (str): path to the server script
        """
        
        server_params = StdioServerParameters(
            command="python",
            args=[server_script_path],
            env=None
        )
        
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        response = await self.session.initialize()
        
        return response
    
    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()
    
    
        
async def main():
    client = MCPClient()
    
    try:
        tools =  await client.connect_to_server("paylink.py")
        
        for tool in tools:
            print(tool)
        
        return tools
    finally:
        await client.cleanup()
        

if __name__ == "__main__":
    asyncio.run(main())