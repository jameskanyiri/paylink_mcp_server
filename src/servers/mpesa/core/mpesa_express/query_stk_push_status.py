import os
import time
import base64
import httpx
from typing import Dict, Any


async def query_stk_push_status(
    access_token: str, checkout_request_id: str
) -> Dict[str, Any]:
    """
    Queries the status of a previously initiated M-Pesa STK Push transaction.

    Args:
        access_token (str): OAuth access token for M-Pesa API.
        checkout_request_id (str): Unique CheckoutRequestID received after
            initiating STK push.

    Returns:
        Dict[str, Any]: A JSON object containing the result of the query.
            Includes ResultCode and status description.
    """

    business_shortcode = os.getenv("BUSINESS_SHORTCODE")
    passkey = os.getenv("PASSKEY")
    base_url = os.getenv("BASE_URL")

    if not all([business_shortcode, passkey, base_url]):
        return {
            "error": {
                "code": "CONFIG_ERROR",
                "message": "Missing required M-Pesa environment variables for query.",
            }
        }

    timestamp = time.strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(
        f"{business_shortcode}{passkey}{timestamp}".encode()
    ).decode()

    payload = {
        "BusinessShortCode": business_shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "CheckoutRequestID": checkout_request_id,
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    url = f"{base_url}/mpesa/stkpushquery/v1/query"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status() # Raises an exception for 4XX/5XX responses
            # If M-Pesa returns an error in a 200 response, it should be handled by the caller
            return response.json()
        except httpx.HTTPStatusError as e:
            return {
                "error": {
                    "code": "HTTP_ERROR",
                    "message": "HTTP request to M-Pesa API failed during status query.",
                    "details": f"Status {e.response.status_code}: {e.response.text}",
                }
            }
        except Exception as e: # Catch other exceptions like network errors, timeouts
            return {
                "error": {
                    "code": "MPESA_API_ERROR",
                    "message": "STK Push status query failed due to an unexpected error.",
                    "details": str(e),
                }
            }
