"""Rotation system: tiers, promotion, banishment, and song selection.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from random import random, choice
from typing import Dict, List, Optional

from src.ai_radio.config import CORE_PLAYLIST_RATIO, DISCOVERY_GRADUATION_PLAYS


class SongTier(Enum):
    CORE = "core"
    DISCOVERY = "discovery"
    BANISHED = "banished"


@dataclass
class SelectedSong:
    id: str
    tier: SongTier


class RotationManager:
    """Manage song tiers and play counts."""

    def __init__(self) -> None:
        self._tiers: Dict[str, SongTier] = {}
        self._plays: Dict[str, int] = {}

    def add_song(self, song_id: str) -> None:
        if song_id not in self._tiers:
            self._tiers[song_id] = SongTier.DISCOVERY
            self._plays[song_id] = 0

    def get_tier(self, song_id: str) -> SongTier:
        return self._tiers.get(song_id, SongTier.DISCOVERY)

    def promote(self, song_id: str) -> None:
        self._tiers[song_id] = SongTier.CORE

    def banish(self, song_id: str) -> None:
        self._tiers[song_id] = SongTier.BANISHED

    def record_play(self, song_id: str) -> None:
        # ensure song tracked
        if song_id not in self._plays:
            self.add_song(song_id)
        self._plays[song_id] += 1
        # auto-promote from discovery after threshold
        if self.get_tier(song_id) == SongTier.DISCOVERY and self._plays[song_id] >= DISCOVERY_GRADUATION_PLAYS:
            self.promote(song_id)

    def _songs_in_tier(self, tier: SongTier) -> List[str]:
        return [s for s, t in self._tiers.items() if t == tier]


# Convenience functions used by tests

def get_next_song(rotation_manager: RotationManager) -> Optional[SelectedSong]:
    """Select next song respecting core/discovery ratio and avoiding banished songs."""
    core_pool = rotation_manager._songs_in_tier(SongTier.CORE)
    discovery_pool = rotation_manager._songs_in_tier(SongTier.DISCOVERY)

    # Decide tier based on ratio
    pick_core = random() < CORE_PLAYLIST_RATIO
    if pick_core:
        pool = core_pool if core_pool else discovery_pool
    else:
        pool = discovery_pool if discovery_pool else core_pool

    if not pool:
        return None

    song_id = choice(pool)
    tier = rotation_manager.get_tier(song_id)
    return SelectedSong(id=song_id, tier=tier)


def banish_song(rotation_manager: RotationManager, song_id: str) -> None:
    rotation_manager.add_song(song_id)
    rotation_manager.banish(song_id)


def promote_song(rotation_manager: RotationManager, song_id: str) -> None:
    rotation_manager.add_song(song_id)
    rotation_manager.promote(song_id)


def record_play(rotation_manager: RotationManager, song_id: str) -> None:
    rotation_manager.record_play(song_id)