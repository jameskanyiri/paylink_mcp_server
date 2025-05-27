import os
import httpx
from typing import Dict


async def generate_dynamic_qr(access_token: str, payload: Dict) -> Dict:
    base_url = os.getenv("BASE_URL")
    if not base_url:
        return {
            "error": {
                "code": "CONFIG_ERROR",
                "message": "Missing BASE_URL environment variable for QR generation.",
            }
        }
    
    url = f"{base_url}/mpesa/qrcode/v1/generate"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status() # Raises an exception for 4XX/5XX responses
            # If M-Pesa returns an error in a 200 response, it should be handled by the caller
            return response.json()
        except httpx.HTTPStatusError as e:
            return {
                "error": {
                    "code": "HTTP_ERROR",
                    "message": "HTTP request to M-Pesa API failed during QR code generation.",
                    "details": f"Status {e.response.status_code}: {e.response.text}",
                }
            }
        except Exception as e: # Catch other exceptions like network errors, timeouts
            return {
                "error": {
                    "code": "MPESA_API_ERROR",
                    "message": "QR code generation failed due to an unexpected error.",
                    "details": str(e),
                }
            }
