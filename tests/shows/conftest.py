import pytest
from types import SimpleNamespace
from pathlib import Path

from src.ai_radio.shows.show_manager import ShowManager, Show, Episode


@pytest.fixture
def shows_directory(tmp_path: Path) -> Path:
    # Create a fake shows directory with one show and multiple episodes
    shows_dir = tmp_path / "shows"
    shows_dir.mkdir()

    shadow = shows_dir / "The Shadow"
    shadow.mkdir()

    # episodes
    (shadow / "episode_1.mp3").write_text("fake")
    (shadow / "episode_2.mp3").write_text("fake")
    (shadow / "episode_3.mp3").write_text("fake")

    return shows_dir


@pytest.fixture
def manager_with_shows(shows_directory: Path) -> ShowManager:
    manager = ShowManager()
    from src.ai_radio.shows.show_manager import scan_shows

    scan_shows(manager, shows_directory)
    return manager


@pytest.fixture
def mock_playback():
    # simple object with an assignable on_item_started hook
    return SimpleNamespace(on_item_started=None)


@pytest.fixture
def show_with_intro(tmp_path: Path) -> Show:
    show_dir = tmp_path / "Spooky Show"
    show_dir.mkdir()
    intro = show_dir / "intro.mp3"
    intro.write_text("intro")
    ep = show_dir / "episode_1.mp3"
    ep.write_text("ep")

    show = Show(name="Spooky Show")
    show.intro_path = intro
    show.episodes = [Episode(episode_number=1, path=ep)]
    return show
