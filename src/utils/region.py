from typing import Tuple

from ..constants import REGION_CHECK_URL
from ..network.client import HttpClient
from ..logger import Logger


class RegionDetector:
    """Region detector"""

    def __init__(self, client: HttpClient, logger: Logger):
        self.client = client
        self.logger = logger

    async def check_cn(self) -> Tuple[bool, str]:
        """Check if in mainland China"""
        try:
            req = await self.client.get(REGION_CHECK_URL)
            body = req.json()
            is_cn = bool(body.get("flag", True))
            country = body.get("country", "Unknown")

            if not is_cn:
                self.logger.info(
                    f"You are using the project outside mainland China ({country}), "
                    "automatically switched back to GitHub official CDN"
                )

            return is_cn, country
        except Exception as e:
            self.logger.warning("Failed to check server location, assuming mainland China by default")
            return True, "CN"
