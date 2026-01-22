from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Deque, Optional


@dataclass
class QueueItem:
    path: Path
    item_type: str = "song"  # e.g., 'song' or 'intro'
    song_id: Optional[str] = None


class PlaybackQueue:
    def __init__(self):
        self._q: Deque[QueueItem] = deque()


# Queue operations

def add_to_queue(queue: PlaybackQueue, item: QueueItem):
    queue._q.append(item)


def insert_next(queue: PlaybackQueue, item: QueueItem):
    queue._q.appendleft(item)


def get_next(queue: PlaybackQueue) -> Optional[QueueItem]:
    if not queue._q:
        return None
    return queue._q.popleft()


def peek_next(queue: PlaybackQueue) -> Optional[QueueItem]:
    if not queue._q:
        return None
    return queue._q[0]


def clear_queue(queue: PlaybackQueue):
    queue._q.clear()


def get_queue_length(queue: PlaybackQueue) -> int:
    return len(queue._q)
