"""Tests for metadata reading."""
import pytest
from pathlib import Path
from src.ai_radio.library.metadata import read_metadata, SongMetadata


class TestReadMetadata:
    """Test metadata reading from files."""

    def test_returns_song_metadata_object(self, sample_mp3_path):
        """Must return a SongMetadata dataclass."""
        result = read_metadata(sample_mp3_path)
        assert isinstance(result, SongMetadata)

    def test_extracts_artist(self, sample_mp3_with_tags):
        """Must extract artist from tags."""
        result = read_metadata(sample_mp3_with_tags)
        assert result.artist is not None
        assert len(result.artist) > 0

    def test_extracts_title(self, sample_mp3_with_tags):
        """Must extract title from tags."""
        result = read_metadata(sample_mp3_with_tags)
        assert result.title is not None
        assert len(result.title) > 0

    def test_handles_missing_metadata(self, sample_mp3_no_tags):
        """Must handle files with no metadata gracefully."""
        result = read_metadata(sample_mp3_no_tags)
        # Should use filename as fallback
        assert result.title is not None

    def test_raises_for_nonexistent_file(self):
        """Must raise SongNotFoundError for missing files."""
        from src.ai_radio.utils.errors import SongNotFoundError

        with pytest.raises(SongNotFoundError):
            read_metadata(Path("/nonexistent/file.mp3"))

    def test_raises_for_non_audio_file(self, tmp_path):
        """Must raise MetadataError for non-audio files."""
        from src.ai_radio.utils.errors import MetadataError

        fake_file = tmp_path / "not_audio.txt"
        fake_file.write_text("This is not audio")
        with pytest.raises(MetadataError):
            read_metadata(fake_file)
