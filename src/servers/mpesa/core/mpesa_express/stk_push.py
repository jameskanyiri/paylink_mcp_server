import os
import time
import httpx
import base64
from typing import Dict, Any


async def initiate_stk_push(
    access_token: str,
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
    business_shortcode = os.getenv("BUSINESS_SHORTCODE")
    passkey = os.getenv("PASSKEY")
    callback_url = os.getenv("CALLBACK_URL")
    base_url = os.getenv("BASE_URL")

    if not all([business_shortcode, passkey, callback_url, base_url]):
        return {"error": "Missing M-Pesa STK environment variables"}

    if not phone_number.startswith("254") or len(phone_number) != 12:
        return {"error": "Invalid phone number format. Must be 254XXXXXXXXX"}

    if len(account_reference) > 12:
        return {"error": "Account reference must be ≤ 12 characters"}

    if len(transaction_desc) > 13:
        return {"error": "Transaction description must be ≤ 13 characters"}

    VALID_TRANSACTION_TYPES = {"CustomerPayBillOnline", "CustomerBuyGoodsOnline"}

    if transaction_type not in VALID_TRANSACTION_TYPES:
        return {
            "error": f"Invalid transaction type {', '.join(VALID_TRANSACTION_TYPES)}"
        }

    timestamp = time.strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(
        f"{business_shortcode}{passkey}{timestamp}".encode()
    ).decode()

    payload = {
        "BusinessShortCode": business_shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": transaction_type,
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": business_shortcode,
        "PhoneNumber": phone_number,
        "CallBackURL": callback_url,
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc,
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    url = f"{base_url}/mpesa/stkpush/v1/processrequest"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": "HTTP Error", "details": e.response.text}
        except Exception as e:
            return {"error": f"STK Push failed: {e}"}
