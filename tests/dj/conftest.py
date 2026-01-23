import pytest
from pathlib import Path
from src.ai_radio.dj.personality import DJ


@pytest.fixture()
def julie_character_card(tmp_path: Path):
    # Use packaged character card from the package
    here = Path(__file__).resolve().parents[1] / ".." / "src" / "ai_radio" / "dj" / "character_cards"
    # Normalizing path via Path
    return Path(here) / "julie.json"


@pytest.fixture()
def mr_vegas_character_card(tmp_path: Path):
    here = Path(__file__).resolve().parents[1] / ".." / "src" / "ai_radio" / "dj" / "character_cards"
    return Path(here) / "mr_new_vegas.json"


@pytest.fixture()
def content_with_intros(tmp_path: Path):
    d = tmp_path / "content"
    d.mkdir()
    # create some intro files
    (d / "julie_song_1_intro.mp3").write_text("dummy")
    (d / "julie_song_1_intro_var2.mp3").write_text("dummy2")
    (d / "mr_new_vegas_song_1_intro.mp3").write_text("dummy3")
    
    # Create time announcements in new directory structure
    time_dir = d / "time" / "julie" / "14-30"
    time_dir.mkdir(parents=True)
    (time_dir / "julie_0.wav").write_text("time1430")
    
    time_dir2 = d / "time" / "julie" / "14-00"
    time_dir2.mkdir(parents=True)
    (time_dir2 / "julie_0.wav").write_text("time1400")
    
    time_dir3 = d / "time" / "julie" / "15-00"
    time_dir3.mkdir(parents=True)
    (time_dir3 / "julie_0.wav").write_text("time1500")
    
    return d


@pytest.fixture()
def content_with_multiple_intros(tmp_path: Path):
    d = tmp_path / "content_multi"
    d.mkdir()
    for i in range(3):
        (d / f"julie_song_1_intro_{i}.mp3").write_text("x")
    return d


@pytest.fixture()
def empty_content_dir(tmp_path: Path):
    return tmp_path / "empty"
