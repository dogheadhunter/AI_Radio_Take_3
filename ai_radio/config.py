from dataclasses import dataclass
import os
from typing import Optional

from .exceptions import ConfigError
from src.ai_radio.config import MUSIC_DIR_ENV, LOG_LEVEL_ENV, LOG_LEVEL as DEFAULT_LOG_LEVEL


@dataclass
class Config:
    """Simple configuration holder for AI Radio Phase 0.

    Reads from environment variables. Keeps things minimal and dependency-free.
    """

    music_dir: Optional[str] = None
    log_level: str = DEFAULT_LOG_LEVEL

    @classmethod
    def from_env(cls) -> "Config":
        music_dir = os.environ.get(MUSIC_DIR_ENV)
        log_level = os.environ.get(LOG_LEVEL_ENV, DEFAULT_LOG_LEVEL)
        return cls(music_dir=music_dir, log_level=log_level)

    def validate(self) -> None:
        """Validate that required config is present and correct.

        Raises:
            ConfigError: if a required value is missing or invalid.
        """
        if not self.music_dir:
            raise ConfigError(f"{MUSIC_DIR_ENV} is not set in the environment")

        if not os.path.isdir(self.music_dir):
            raise ConfigError(f"{MUSIC_DIR_ENV} does not point to a directory: {self.music_dir}")
