from typing import List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DepotInfo:
    """Depot information"""

    depot_id: str
    decryption_key: str
    manifest_ids: List[str] = None

    def __post_init__(self):
        if self.manifest_ids is None:
            self.manifest_ids = []


@dataclass
class RepoInfo:
    """GitHub repository information"""

    name: str
    last_update: datetime
    sha: str


@dataclass
class AppConfig:
    """Application configuration"""

    github_token: str = ""
    custom_steam_path: str = ""
    debug_mode: bool = False
    logging_files: bool = True
