import vdf
from typing import List

from .base import UnlockTool
from ..models import DepotInfo


class GreenLuma(UnlockTool):
    """Implementation of GreenLuma unlock tool"""

    async def setup(self, depot_data: List[DepotInfo], app_id: str, **kwargs) -> bool:
        """Setup GreenLuma unlock"""
        applist_dir = self.steam_path / "AppList"
        applist_dir.mkdir(exist_ok=True)

        # Remove existing .txt files
        for f in applist_dir.glob("*.txt"):
            f.unlink()

        # Write new depot files
        for idx, depot in enumerate(depot_data, 1):
            (applist_dir / f"{idx}.txt").write_text(depot.depot_id)

        config_path = self.steam_path / "config" / "config.vdf"
        try:
            # Read existing config
            with open(config_path, "r", encoding="utf-8") as f:
                content = vdf.loads(f.read())

            # Update depots with decryption keys
            content.setdefault("depots", {}).update(
                {
                    depot.depot_id: {"DecryptionKey": depot.decryption_key}
                    for depot in depot_data
                }
            )

            # Write back updated config
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(vdf.dumps(content))

            return True
        except Exception:
            return False
