from typing import Tuple

from .config import Config
from .exceptions import ConfigError
from src.ai_radio.config import ENV_OK_MSG


def validate_env() -> Tuple[bool, str]:
    cfg = Config.from_env()
    try:
        cfg.validate()
    except ConfigError as exc:
        return False, str(exc)
    return True, ENV_OK_MSG
