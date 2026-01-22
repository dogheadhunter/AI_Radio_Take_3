import pytest
from pathlib import Path
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC


@pytest.fixture
def tmp_music_dir(tmp_path):
    music_dir = tmp_path / "music"
    music_dir.mkdir()
    return music_dir


@pytest.fixture
def sample_mp3_path(tmp_music_dir):
    mp3_path = tmp_music_dir / "sample.mp3"
    # Minimal MPEG header (not a full MP3 but sufficient for mutagen to attach ID3)
    mp3_path.write_bytes(b"\xff\xfb\x90\x00" + b"\x00" * 1024)
    return mp3_path


@pytest.fixture
def sample_mp3_with_tags(sample_mp3_path):
    # Add ID3 tags to the existing minimal MP3 file
    id3 = ID3()
    id3.add(TIT2(encoding=3, text="Test Title"))
    id3.add(TPE1(encoding=3, text="Test Artist"))
    id3.add(TALB(encoding=3, text="Test Album"))
    id3.add(TDRC(encoding=3, text="1945"))
    id3.save(sample_mp3_path)
    return sample_mp3_path


@pytest.fixture
def sample_mp3_no_tags(sample_mp3_path):
    # Ensure file has no tags
    try:
        ID3(sample_mp3_path).delete()
    except Exception:
        pass
    return sample_mp3_path
