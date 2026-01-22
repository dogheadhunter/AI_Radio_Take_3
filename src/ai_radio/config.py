from pathlib import Path

# Project root (where this repo lives)
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Directory paths
MUSIC_LIBRARY_PATH = Path("SET_THIS_TO_YOUR_MUSIC_FOLDER")
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
ASSETS_DIR = PROJECT_ROOT / "assets"
GENERATED_DIR = DATA_DIR / "generated"
VOICE_REFERENCES_DIR = ASSETS_DIR / "voice_references"

# Catalog files
CATALOG_FILE = DATA_DIR / "catalog.json"
BANISHED_FILE = DATA_DIR / "banished_songs.txt"
FLAGGED_FILE = DATA_DIR / "flagged_intros.txt"

# DJ Settings
DJ_JULIE_SHIFT_START = 6   # 6 AM
DJ_JULIE_SHIFT_END = 19    # 7 PM
DJ_HANDOFF_HOUR = 19       # 7 PM

# Rotation settings
CORE_PLAYLIST_RATIO = 0.70  # 70% core, 30% discovery
DISCOVERY_GRADUATION_PLAYS = 5  # Plays before auto-promotion

# Time announcement settings
TIME_ANNOUNCE_INTERVAL_MINUTES = 30

# Weather settings
WEATHER_TIMES = [6, 12, 17]  # 6 AM, 12 PM, 5 PM
WEATHER_CACHE_MINUTES = 30

# Radio show settings
RADIO_SHOW_HOUR = 20  # 8 PM

# Signal detection
SIGNAL_THRESHOLD = 0.5  # Default threshold for signal detection

# Environment variable names
MUSIC_DIR_ENV = "AI_RADIO_MUSIC_DIR"
LOG_LEVEL_ENV = "AI_RADIO_LOG_LEVEL"
ENV_OK_MSG = "Environment OK"

# Logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"
