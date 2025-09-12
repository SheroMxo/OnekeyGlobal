import traceback
from typing import List, Dict, Tuple

from . import __version__, __author__, __website__
from .constants import BANNER, REPO_LIST
from .config import ConfigManager
from .logger import Logger
from .models import DepotInfo
from .network.client import HttpClient
from .network.github import GitHubAPI
from .utils.steam import parse_key_file, parse_manifest_filename
from .tools.steamtools import SteamTools
from .tools.greenluma import GreenLuma


class OnekeyApp:
    """Onekey main application"""

    def __init__(self):
        self.config = ConfigManager()
        self.logger = Logger(
            "Onekey",
            debug_mode=self.config.app_config.debug_mode,
            log_file=self.config.app_config.logging_files,
        )
        self.client = HttpClient()
        self.github = GitHubAPI(self.client, self.config.github_headers, self.logger)

    def show_banner(self):
        """Show startup banner"""
        self.logger.info(BANNER)
        self.logger.info(
            f"This program source code is open under GPL 2.0 license on GitHub"
        )
        self.logger.info(
            f"Author: {__author__} | Version: {__version__} | Website: {__website__}"
        )
        self.logger.info("Project repository: GitHub: https://github.com/ikunshare/Onekey")
        self.logger.warning("ikunshare.top | Reselling strictly prohibited")
        self.logger.warning(
            "Note: Make sure Windows 10/11 is installed and Steam; SteamTools/GreenLuma are properly configured"
        )
        if not self.config.app_config.github_token:
            self.logger.warning("If using a proxy, you must configure a Token.")

    async def handle_depot_files(
        self, app_id: str
    ) -> Tuple[List[DepotInfo], Dict[str, List[str]]]:
        """Handle depot files"""
        depot_list = []
        depot_map = {}

        repo_info = await self.github.get_latest_repo_info(REPO_LIST, app_id)
        if not repo_info:
            return depot_list, depot_map

        self.logger.info(f"Currently selected manifest repository: https://github.com/{repo_info.name}")
        self.logger.info(f"Last update time of this manifest branch: {repo_info.last_update}")

        branch_url = f"https://api.github.com/repos/{repo_info.name}/branches/{app_id}"
        branch_res = await self.client.get(
            branch_url, headers=self.config.github_headers
        )
        branch_res.raise_for_status()

        tree_url = branch_res.json()["commit"]["commit"]["tree"]["url"]
        tree_res = await self.client.get(tree_url)
        tree_res.raise_for_status()

        depot_cache = self.config.steam_path / "depotcache"
        depot_cache.mkdir(exist_ok=True)

        for item in tree_res.json()["tree"]:
            file_path = item["path"]

            if file_path.endswith(".manifest"):
                save_path = depot_cache / file_path
                if save_path.exists():
                    self.logger.warning(f"Manifest already exists: {save_path}")
                    continue

                content = await self.github.fetch_file(
                    repo_info.name, repo_info.sha, file_path
                )
                save_path.write_bytes(content)
                self.logger.info(f"Manifest downloaded successfully: {file_path}")

                depot_id, manifest_id = parse_manifest_filename(file_path)
                if depot_id and manifest_id:
                    depot_map.setdefault(depot_id, []).append(manifest_id)

            elif "key.vdf" in file_path.lower():
                key_content = await self.github.fetch_file(
                    repo_info.name, repo_info.sha, file_path
                )
                depot_list.extend(parse_key_file(key_content))

        for depot_id in depot_map:
            depot_map[depot_id].sort(key=lambda x: int(x), reverse=True)

        return depot_list, depot_map

    async def run(self, app_id: str):
        """Run main program"""
        try:
            await self.github.check_rate_limit()

            self.logger.info(f"Processing game {app_id}...")
            depot_data, depot_map = await self.handle_depot_files(app_id)

            if not depot_data:
                self.logger.error("No manifest found for this game")
                return

            print("\nPlease choose unlock tool:")
            print("1. SteamTools")
            print("2. GreenLuma")

            choice = input("Enter your choice (1/2): ").strip()

            if choice == "1":
                tool = SteamTools(self.config.steam_path)

                version_lock = False
                lock_choice = input(
                    "Do you want to lock the version (recommended when using SteamAutoCracks/ManifestHub)? (y/n): "
                ).lower()
                if lock_choice == "y":
                    version_lock = True

                success = await tool.setup(
                    depot_data, app_id, depot_map=depot_map, version_lock=version_lock
                )
            elif choice == "2":
                tool = GreenLuma(self.config.steam_path)
                success = await tool.setup(depot_data, app_id)
            else:
                self.logger.error("Invalid choice")
                return

            if success:
                self.logger.info("Game unlock configuration successful!")
                self.logger.info("Restart Steam to take effect")
            else:
                self.logger.error("Configuration failed")

        except Exception as e:
            self.logger.error(f"Runtime error: {traceback.format_exc()}")
        finally:
            await self.client.close()


async def main():
    """Program entry point"""
    app = OnekeyApp()
    app.show_banner()

    app_id = input("\nEnter game AppID: ").strip()

    app_id_list = [id for id in app_id.split("-") if id.isdigit()]
    if not app_id_list:
        app.logger.error("Invalid App ID")
        return

    await app.run(app_id_list[0])
