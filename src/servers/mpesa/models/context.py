from dataclasses import dataclass
import asyncio


@dataclass
class MPesaContext:
    """Context for managing MPesa Integration"""

    access_token: str
    expires_at: float
    refresh_task: asyncio.Task | None
