import os
import httpx
from typing import Dict

async def generate_dynamic_qr(access_token: str, payload: Dict) -> Dict:
    base_url = os.getenv("BASE_URL")
    url = f"{base_url}/mpesa/qrcode/v1/generate"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
