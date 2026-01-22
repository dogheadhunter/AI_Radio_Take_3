"""Tests for show manager."""
import pytest
from pathlib import Path
from src.ai_radio.shows.show_manager import (
    ShowManager,
    scan_shows,
    get_next_episode,
    mark_episode_played,
    Show,
    Episode,
)


class TestScanShows:
    """Test show scanning."""

    def test_finds_show_directories(self, shows_directory):
        """Must find show directories."""
        manager = ShowManager()
        shows = scan_shows(manager, shows_directory)
        assert len(shows) > 0

    def test_finds_episodes_in_show(self, shows_directory):
        """Must find episode files in each show."""
        manager = ShowManager()
        shows = scan_shows(manager, shows_directory)

        for show in shows:
            assert len(show.episodes) > 0


class TestEpisodeSelection:
    """Test episode selection."""

    def test_returns_first_unplayed(self, manager_with_shows):
        """Must return first unplayed episode."""
        episode = get_next_episode(manager_with_shows, show_name="The Shadow")
        assert episode.episode_number == 1

    def test_advances_after_played(self, manager_with_shows):
        """Must return next episode after marking played."""
        ep1 = get_next_episode(manager_with_shows, show_name="The Shadow")
        mark_episode_played(manager_with_shows, ep1)

        ep2 = get_next_episode(manager_with_shows, show_name="The Shadow")
        assert ep2.episode_number == 2

    def test_loops_after_all_played(self, manager_with_shows):
        """Must loop back to episode 1 after all played."""
        show = manager_with_shows.get_show("The Shadow")

        # Play all episodes
        for ep in show.episodes:
            mark_episode_played(manager_with_shows, ep)

        # Next should be episode 1 again
        next_ep = get_next_episode(manager_with_shows, show_name="The Shadow")
        assert next_ep.episode_number == 1
