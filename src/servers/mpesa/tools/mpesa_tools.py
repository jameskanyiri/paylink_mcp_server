import json
from typing import Dict, Any
from mcp.server.fastmcp import Context
from src.servers.mpesa.models.context import MPesaContext
from src.servers.mpesa.core.stk_push import initiate_stk_push


class MpesaTools:
    def __init__(self, mcp) -> None:
        """
        Initializes the MpesaTools class and registers available tools.

        Args:
            mcp: The MCP server instance to register the tools with.
        """
        self.mcp = mcp

        # Register tools during initialization
        self.register_tools()

    def register_tools(self):
        """
        Registers available tools
        """

        @self.mcp.tool()
        async def stk_push(
            ctx: Context,
            phone_number: str,
            amount: int,
            account_reference: str,
            transaction_desc: str,
            transaction_type: str,
        ) -> Dict[str, Any]:
            """
            Initiates an M-Pesa STK Push (Sim Tool Kit) transaction, which allows a merchant to request a customer to authorize a payment through M-Pesa.

            This tool triggers the M-Pesa Lipa na M-Pesa Online API (STK Push), which sends a payment request to the customer's M-Pesa registered phone number. 
            The customer receives a prompt on their phone to enter their M-Pesa PIN to authorize and complete the payment.

            Args:
                phone_number (str): The mobile number to which the STK Push prompt will be sent (should be an M-Pesa registered number).
                amount (int): The amount to be paid, in integer value.
                account_reference (str): A reference string for the account being charged, displayed to the customer in the STK prompt.
                transaction_desc (str): A brief description of the transaction, displayed in the STK prompt.
                transaction_type (str): The type of transaction being processed (e.g., "CustomerPayBillOnline" for pay bill transactions, or "CustomerBuyGoodsOnline" for goods purchases).

            Returns:
                Dict[str, Any]: A JSON object containing the result of the request. On success, includes the transaction's status and details. In case of failure, an error message will be returned.

            """
            try:
                # Access the M-Pesa context (which includes necessary details like access token)
                mpesa_ctx: MPesaContext = ctx.request_context.lifespan_context
                
                # Call the function that initiates the STK push and get the response
                response = await initiate_stk_push(
                    mpesa_ctx.access_token,
                    phone_number,
                    amount,
                    account_reference,
                    transaction_desc,
                    transaction_type
                )
                # Return the response as a formatted JSON string
                return json.dumps(response, indent=2)
            except Exception as e:
                # Handle any exceptions that occur and return an error message
                return {"error": f"Failed to initiate STK push: {str(e)}"}