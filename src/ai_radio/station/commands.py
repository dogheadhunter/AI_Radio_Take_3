"""
Command handler for user input during playback.
"""
from enum import Enum, auto
from typing import Optional, TYPE_CHECKING
import sys
import threading

if TYPE_CHECKING:
    from src.ai_radio.station.controller import StationController


class Command(Enum):
    QUIT = auto()
    PAUSE = auto()
    RESUME = auto()
    SKIP = auto()
    BANISH = auto()
    FLAG = auto()
    PROMOTE = auto()
    VOLUME_UP = auto()
    VOLUME_DOWN = auto()


KEY_MAP = {
    'q': Command.QUIT,
    'p': Command.PAUSE,
    's': Command.SKIP,
    'b': Command.BANISH,
    'f': Command.FLAG,
    'r': Command.PROMOTE,
    '+': Command.VOLUME_UP,
    '-': Command.VOLUME_DOWN,
}


def parse_key(key: str) -> Optional[Command]:
    return KEY_MAP.get(key.lower())


def execute_command(command: Command, controller: 'StationController') -> None:
    from src.ai_radio.utils.logging import setup_logging
    logger = setup_logging("commands")

    if command == Command.QUIT:
        logger.info("Quit command received")
        controller.stop()

    elif command == Command.PAUSE:
        if controller.is_playing:
            logger.info("Pausing playback")
            controller.pause()
        else:
            logger.info("Resuming playback")
            controller.resume()

    elif command == Command.SKIP:
        logger.info(f"Skipping:  {getattr(controller, 'current_song_display', '')}")
        controller.skip()

    elif command == Command.BANISH:
        song_id = getattr(controller, 'current_song_id', None)
        if song_id:
            logger.info(f"Banishing: {getattr(controller, 'current_song_display', '')}")
            controller.banish_song(song_id)
            controller.skip()

    elif command == Command.FLAG:
        intro_path = getattr(controller, 'current_intro_path', None)
        if intro_path:
            logger.info(f"Flagging intro for regeneration: {intro_path}")
            controller.flag_intro(intro_path)

    elif command == Command.PROMOTE:
        song_id = getattr(controller, 'current_song_id', None)
        if song_id:
            logger.info(f"Promoting: {getattr(controller, 'current_song_display', '')}")
            controller.promote_song(song_id)


class CommandHandler:
    def __init__(self, controller: 'StationController'):
        self.controller = controller
        self.running = False
        self.thread: Optional[threading.Thread] = None

    def start(self) -> None:
        self.running = True
        self.thread = threading.Thread(target=self._input_loop, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.running = False

    def _input_loop(self) -> None:
        if sys.platform == 'win32':
            import msvcrt
            while self.running:
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode('utf-8', errors='ignore')
                    command = parse_key(key)
                    if command:
                        execute_command(command, self.controller)
        else:
            # Not implementing non-Windows input for MVP
            while self.running:
                # Non-blocking read not implemented; sleep to avoid busy-loop
                import time
                time.sleep(0.1)
