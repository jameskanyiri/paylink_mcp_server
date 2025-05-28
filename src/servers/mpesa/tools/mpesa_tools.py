from typing import Dict, Any
from mcp.server.fastmcp import Context
from src.servers.mpesa.models.context import MPesaContext
from src.servers.mpesa.core.mpesa_express.stk_push import initiate_stk_push
from src.servers.mpesa.core.mpesa_express.query_stk_push_status import (
    query_stk_push_status,
)
from src.servers.mpesa.core.mpesa_qr.generate_dynamic_qr import generate_dynamic_qr


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
            Initiates an M-Pesa STK Push (Sim Tool Kit) transaction, allowing
            a merchant to request a customer to authorize a payment via M-Pesa.

            This tool triggers the M-Pesa Lipa na M-Pesa Online API (STK Push),
            sending a payment request to the customer's M-Pesa registered
            phone number. The customer then enters their M-Pesa PIN to
            authorize and complete the payment.

            Args:
                phone_number (str): Mobile number for STK Push prompt
                    (M-Pesa registered).
                amount (int): Amount to be paid (integer).
                account_reference (str): Account reference displayed to customer
                    in STK prompt.
                transaction_desc (str): Brief transaction description shown in
                    STK prompt.
                transaction_type (str): Transaction type, e.g.,
                    "CustomerPayBillOnline" or "CustomerBuyGoodsOnline".

            Returns:
                Dict[str, Any]: JSON object with request result. On success,
                    includes transaction status/details. On failure, returns
                    an error message.
            """
            try:
                # Access M-Pesa context (includes access token)
                mpesa_ctx: MPesaContext = ctx.request_context.lifespan_context

                # Call the function that initiates the STK push and get the response
                response = await initiate_stk_push(
                    mpesa_ctx.access_token,
                    phone_number,
                    amount,
                    account_reference,
                    transaction_desc,
                    transaction_type,
                )
                # Return the response directly
                return response
            except Exception as e:
                # Handle any exceptions that occur and return an error message
                return {
                    "error": {
                        "code": "TOOL_EXECUTION_ERROR",
                        "message": "Failed to execute STK push tool.",
                        "details": str(e),
                    }
                }

        # STK PUSH STATUS QUERY TOOL
        @self.mcp.tool()
        async def stk_push_status(
            ctx: Context,
            checkout_request_id: str,
        ) -> Dict[str, Any]:
            """
            Queries status of an M-Pesa STK Push transaction using CheckoutRequestID.

            Checks if a previously initiated Lipa na M-Pesa Online transaction
            succeeded, failed, or is pending.

            Args:
                checkout_request_id (str): Unique ID from M-Pesa during STK push
                    initiation.

            Returns:
                Dict[str, Any]: JSON object with transaction status (ResultCode
                    and ResultDesc).
            """
            try:
                mpesa_ctx: MPesaContext = ctx.request_context.lifespan_context

                response = await query_stk_push_status(
                    mpesa_ctx.access_token, checkout_request_id
                )
                # Return the response directly
                return response
            except Exception as e:
                return {
                    "error": {
                        "code": "TOOL_EXECUTION_ERROR",
                        "message": "Failed to execute STK push status query tool.",
                        "details": str(e),
                    }
                }

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
            Generates Dynamic M-PESA QR Code for LIPA NA M-PESA (LNM) payments
            via Safaricom's QR API.

            Enables M-PESA customers with MySafaricom App or M-PESA App to scan
            a QR Code and pay a merchant's till/business number. Captures
            metadata (amount, ref no, CPI) and returns base64 QR image.

            Args:
                merchant_name (str): M-PESA merchant/company name shown to customer.
                    Example: "TEST SUPERMARKET"
                ref_no (str): Reference/invoice number for the transaction.
                    Example: "Invoice-123"
                amount (int): Total transaction amount in KES.
                    Example: 2000
                trx_code (str): Transaction type. Supported:
                    - "BG": Buy Goods (Pay Merchant)
                    - "WA": Withdraw Cash at Agent Till
                    - "PB": Paybill
                    - "SM": Send Money to MSISDN
                    - "SB": Send to Business (CPI in MSISDN format)
                cpi (str): Credit Party Identifier (till, paybill, or MSISDN).
                    Example: "174379"
                size (str, optional): QR image size in pixels (square). Default "300".

            Returns:
                Dict[str, Any]: Dictionary with:
                    - ResponseCode (str): Unique transaction code
                        (e.g., "AG_20201212_xxxxxx").
                    - RequestID (str): Safaricom request tracking ID.
                    - ResponseDescription (str): Status
                        (e.g., "QR Code Successfully Generated.").
                    - QRCode (str): Base64-encoded PNG QR image.

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
                return {
                    "error": {
                        "code": "TOOL_EXECUTION_ERROR",
                        "message": "Failed to execute QR code generation tool.",
                        "details": str(e),
                    }
                }
