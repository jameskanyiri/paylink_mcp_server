import os
import base64
import httpx
import asyncio
import time
from dotenv import load_dotenv
from src.servers.mpesa.models.context import MPesaContext

load_dotenv(override=True)


async def get_access_token():
    consumer_key = os.getenv("MPESA_CONSUMER_KEY")
    consumer_secret = os.getenv("MPESA_CONSUMER_SECRET")
    base_url = os.getenv("BASE_URL")

    if not consumer_key or not consumer_secret or not base_url:
        raise ValueError("Missing M-Pesa environment variables.")

    auth_string = f"{consumer_key}:{consumer_secret}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()

    url = f"{base_url}/oauth/v1/generate"
    headers = {"Authorization": f"Basic {encoded_auth}"}
    params = {"grant_type": "client_credentials"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return {
            "access_token": data["access_token"],
            "expires_in": int(data["expires_in"]),
        }


async def refresh_access_token(context: MPesaContext):
    while True:
        sleep_for = max(context.expires_at - time.time() - 60, 60)
        await asyncio.sleep(sleep_for)
        try:
            print("Refreshing M-Pesa access token...")
            token_data = await get_access_token()
            context.access_token = token_data["access_token"]
            context.expires_at = time.time() + token_data["expires_in"]
        except Exception as e:
            print(f"Token refresh failed: {e}")
            await asyncio.sleep(30)
