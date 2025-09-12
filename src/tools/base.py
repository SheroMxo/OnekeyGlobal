from abc import ABC, abstractmethod
from typing import List
from pathlib import Path

from ..models import DepotInfo


class UnlockTool(ABC):
    """Base class for unlock tools"""

    def __init__(self, steam_path: Path):
        self.steam_path = steam_path

    @abstractmethod
    async def setup(self, depot_data: List[DepotInfo], app_id: str, **kwargs) -> bool:
        """Setup unlock"""
        pass
