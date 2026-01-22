"""Tests for library scanning."""
import pytest
from pathlib import Path
from src.ai_radio.library.scanner import scan_library, ScanResult
from src.ai_radio.library.metadata import SongMetadata
from src.ai_radio.utils.errors import MusicLibraryError


def test_returns_scan_result(tmp_path):
    d = tmp_path / "music"
    d.mkdir()
    result = scan_library(d)
    assert isinstance(result, ScanResult)


def test_finds_mp3_files(tmp_path):
    d = tmp_path / "music"
    d.mkdir()
    # create some mock mp3 files
    (d / "a.mp3").write_bytes(b"\x00")
    (d / "b.mp3").write_bytes(b"\x00")
    result = scan_library(d)
    assert result.total_files >= 2


def test_returns_song_metadata_list(tmp_path):
    d = tmp_path / "music"
    d.mkdir()
    f = d / "song.mp3"
    f.write_bytes(b"\xff\xfb\x90\x00" + b"\x00" * 1024)
    # add minimal ID3 tags so read_metadata can parse
    from mutagen.id3 import ID3, TIT2, TPE1

    id3 = ID3()
    id3.add(TIT2(encoding=3, text="Title"))
    id3.add(TPE1(encoding=3, text="Artist"))
    id3.save(f)

    result = scan_library(d)
    assert len(result.songs) > 0
    assert all(isinstance(s, SongMetadata) for s in result.songs)


def test_tracks_failed_files(tmp_path):
    d = tmp_path / "music"
    d.mkdir()
    good = d / "good.mp3"
    bad = d / "bad.mp3"
    good.write_bytes(b"\xff\xfb\x90\x00" + b"\x00" * 1024)
    bad.write_text("not audio")

    # add ID3 to good
    from mutagen.id3 import ID3, TIT2, TPE1

    id3 = ID3()
    id3.add(TIT2(encoding=3, text="Title"))
    id3.add(TPE1(encoding=3, text="Artist"))
    id3.save(good)

    result = scan_library(d)
    assert len(result.failed_files) >= 1


def test_raises_for_nonexistent_directory():
    with pytest.raises(MusicLibraryError):
        scan_library(Path("/nonexistent/directory"))


def test_handles_empty_directory(tmp_path):
    result = scan_library(tmp_path)
    assert result.total_files == 0
    assert len(result.songs) == 0
