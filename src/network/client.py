"""HTTP client module"""

import httpx
from typing import Optional, Dict


class HttpClient:
    """HTTP client wrapper"""

    def __init__(self):
        self._client = httpx.AsyncClient(verify=False, timeout=30.0)

    async def get(self, url: str, headers: Optional[Dict] = None) -> httpx.Response:
        """GET request"""
        return await self._client.get(url, headers=headers)

    async def close(self):
        """Close the client"""
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
