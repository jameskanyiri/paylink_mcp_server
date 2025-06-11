import json
from typing import Dict, Any
from mcp.server.fastmcp import Context
from src.servers.mpesa.models.context import MPesaContext
from src.servers.mpesa.core.mpesa_express.stk_push import initiate_stk_push
from src.servers.mpesa.core.mpesa_express.query_stk_push_status import (
    query_stk_push_status,
)
from src.servers.mpesa.core.mpesa_qr.generate_dynamic_qr import generate_dynamic_qr
from src.servers.mpesa.core.c2b.initiate_c2b_payment import initiate_c2b_payment


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
        
       

        # STK PUSH TOOL
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
                
                print("Initiating STK push...")

                # Call the function that initiates the STK push and get the response
                response = await initiate_stk_push(
                    mpesa_ctx.access_token,
                    phone_number,
                    amount,
                    account_reference,
                    transaction_desc,
                    transaction_type,
                )
                # Return the response as a formatted JSON string
                return json.dumps(response, indent=2)
            except Exception as e:
                # Handle any exceptions that occur and return an error message
                return {"error": f"Failed to initiate STK push: {str(e)}"}

        # STK PUSH STATUS QUERY TOOL
        @self.mcp.tool()
        async def stk_push_status(
            ctx: Context,
            checkout_request_id: str,
        ) -> Dict[str, Any]:
            """
            Queries the status of an M-Pesa STK Push transaction using the CheckoutRequestID.

            This tool checks whether a previously initiated Lipa na M-Pesa Online transaction was successful, failed, or is still pending.

            Args:
                checkout_request_id (str): The unique ID returned by M-Pesa during STK push initiation.

            Returns:
                Dict[str, Any]: A JSON object with transaction status including ResultCode and ResultDesc.
            """
            try:
                mpesa_ctx: MPesaContext = ctx.request_context.lifespan_context

                response = await query_stk_push_status(
                    mpesa_ctx.access_token, checkout_request_id
                )
                return json.dumps(response, indent=2)
            except Exception as e:
                return {"error": f"Failed to query STK push status: {str(e)}"}

        # GENERATE QR CODE
        @self.mcp.tool()
        async def generate_qr_code(
            ctx: Context,
            merchant_name: str,
            ref_no: str,
            amount: int,
            trx_code: str,
            cpi: str,
            size: str = "300",
        ) -> Dict[str, Any]:
            """
            Generates a Dynamic M-PESA QR Code for LIPA NA M-PESA (LNM) merchant payments using Safaricom's QR API.

            This MCP tool enables Safaricom M-PESA customers using the MySafaricom App or M-PESA App to scan
            a QR Code and pay directly to a merchant's till or business number. It captures key metadata such as
            amount, reference number, and credit party identifier (CPI) — and returns a base64-encoded QR image.

            Args:
                merchant_name (str): Name of the M-PESA merchant or company as shown to the customer.
                    Example: "TEST SUPERMARKET"
                ref_no (str): Reference or invoice number to identify the transaction.
                    Example: "Invoice-123"
                amount (int): Total amount for the transaction in Kenyan Shillings.
                    Example: 2000
                trx_code (str): Type of transaction. Supported values include:
                    - "BG": Buy Goods (Pay Merchant)
                    - "WA": Withdraw Cash at Agent Till
                    - "PB": Paybill
                    - "SM": Send Money to MSISDN
                    - "SB": Send to Business (CPI in MSISDN format)
                cpi (str): Credit Party Identifier — till number, paybill, or MSISDN of merchant.
                    Example: "174379"
                size (str, optional): Size in pixels of the QR image (square). Default is "300".

            Returns:
                Dict[str, Any]: A dictionary containing:
                    - ResponseCode (str): Unique transaction code, e.g. "AG_20201212_xxxxxx"
                    - RequestID (str): Safaricom request tracking ID
                    - ResponseDescription (str): Status message, e.g. "QR Code Successfully Generated."
                    - QRCode (str): Base64-encoded PNG image of the QR code (can be rendered or stored)

            """
            try:
                mpesa_ctx: MPesaContext = ctx.request_context.lifespan_context

                payload = {
                    "MerchantName": merchant_name,
                    "RefNo": ref_no,
                    "Amount": amount,
                    "TrxCode": trx_code,
                    "CPI": cpi,
                    "Size": size,
                }

                response = await generate_dynamic_qr(mpesa_ctx.access_token, payload)
                return response
            except Exception as e:
                return {"error": f"Failed to generate QR code: {str(e)}"}
            
            
        #INITIATE CUSTOMER TO BUSINESS
        @self.mcp.tool()
        async def c2b_payment(
            amount: int,
            account_number: str,
        ) -> Dict[str, Any]:
            """
            Generates M-Pesa C2B payment instructions for manual user payment via Paybill.

            Args:
                amount (int): The amount the user should pay.
                account_number (str): The reference/account number that identifies the payment.

            Returns:
                Dict[str, Any]: Payment instructions for the user.
            """
            
            try:
                

                response = await initiate_c2b_payment(amount, account_number)
                return response
            except Exception as e:
                return {"error": f"Failed to generate QR code: {str(e)}"}
            
