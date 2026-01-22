"""Tests for rotation system."""
import pytest
from src.ai_radio.library.rotation import (
    RotationManager,
    SongTier,
    get_next_song,
    banish_song,
    promote_song,
    record_play,
)


class MockSong:
    def __init__(self, id: str):
        self.id = id


@pytest.fixture
def mock_song():
    return MockSong("song_1")


@pytest.fixture
def rotation_manager():
    rm = RotationManager()
    s = MockSong("song_1")
    rm.add_song(s.id)
    return rm


@pytest.fixture
def rotation_manager_with_songs():
    rm = RotationManager()
    # add multiple songs
    for i in range(5):
        rm.add_song(f"song_{i}")
    return rm


@pytest.fixture
def rotation_manager_with_mixed_tiers():
    rm = RotationManager()
    # create 20 songs, promote half to CORE
    for i in range(20):
        sid = f"s{i}"
        rm.add_song(sid)
        if i % 2 == 0:
            rm.promote(sid)
    return rm


class TestSongTiers:
    def test_new_songs_are_discovery(self, rotation_manager, mock_song):
        song = mock_song
        tier = rotation_manager.get_tier(song.id)
        assert tier == SongTier.DISCOVERY

    def test_promoted_songs_are_core(self, rotation_manager, mock_song):
        song = mock_song
        promote_song(rotation_manager, song.id)
        tier = rotation_manager.get_tier(song.id)
        assert tier == SongTier.CORE

    def test_banished_songs_are_banished(self, rotation_manager, mock_song):
        song = mock_song
        banish_song(rotation_manager, song.id)
        tier = rotation_manager.get_tier(song.id)
        assert tier == SongTier.BANISHED


class TestAutomaticGraduation:
    def test_graduates_after_threshold(self, rotation_manager):
        from src.ai_radio.config import DISCOVERY_GRADUATION_PLAYS
        song = MockSong("song_2")
        rotation_manager.add_song(song.id)

        for _ in range(DISCOVERY_GRADUATION_PLAYS):
            record_play(rotation_manager, song.id)

        tier = rotation_manager.get_tier(song.id)
        assert tier == SongTier.CORE

    def test_does_not_graduate_early(self, rotation_manager):
        from src.ai_radio.config import DISCOVERY_GRADUATION_PLAYS
        song = MockSong("song_3")
        rotation_manager.add_song(song.id)

        for _ in range(DISCOVERY_GRADUATION_PLAYS - 1):
            record_play(rotation_manager, song.id)

        tier = rotation_manager.get_tier(song.id)
        assert tier == SongTier.DISCOVERY


class TestSongSelection:
    def test_never_selects_banished(self, rotation_manager_with_songs):
        banished_id = "banished_song"
        banish_song(rotation_manager_with_songs, banished_id)

        selected = [get_next_song(rotation_manager_with_songs) for _ in range(100)]
        # filter out None selections just in case
        selected_ids = [s.id for s in selected if s is not None]
        assert banished_id not in selected_ids

    def test_respects_core_ratio_approximately(self, rotation_manager_with_mixed_tiers):
        from src.ai_radio.config import CORE_PLAYLIST_RATIO

        selections = [get_next_song(rotation_manager_with_mixed_tiers) for _ in range(1000)]
        selections = [s for s in selections if s is not None]
        core_count = sum(1 for s in selections if s.tier == SongTier.CORE)

        expected = CORE_PLAYLIST_RATIO * len(selections)
        # allow a 10% margin of error relative to total selections
        assert abs(core_count - expected) < 0.10 * len(selections)
