import json
from pathlib import Path

import pytest

from src.ai_radio.generation.lyrics_parser import (
    parse_lyrics_file,
    extract_lyrics_context,
    match_lyrics_to_catalog,
    LyricsData,
)


def test_parse_lyrics_file_basic(tmp_path: Path):
    content = (
        "Title: Test Song\n"
        "Artist: Test Artist\n"
        "Provider: foo\n"
        "Instrumental: False\n"
        "--------------------------------------------------------------------------------\n"
        "This is the first line of the song.\n"
        "This is the chorus.\n"
    )
    f = tmp_path / "test_song.txt"
    f.write_text(content, encoding="utf-8")

    ld = parse_lyrics_file(f)
    assert isinstance(ld, LyricsData)
    assert ld.title == "Test Song"
    assert ld.artist == "Test Artist"
    assert "first line" in ld.lyrics
    assert not ld.is_instrumental


def test_parse_instrumental_file(tmp_path: Path):
    content = (
        "Title: Quiet Piece\n"
        "Artist: Silent Band\n"
        "Instrumental: True\n"
        "--------------------------------------------------------------------------------\n"
    )
    f = tmp_path / "quiet.txt"
    f.write_text(content, encoding="utf-8")

    ld = parse_lyrics_file(f)
    assert ld is not None
    assert ld.is_instrumental
    assert ld.lyrics == ""


def test_parse_malformed_file_infer_from_filename(tmp_path: Path):
    content = "Just some text without metadata or separator"
    f = tmp_path / "A Song by An Artist.txt"
    f.write_text(content, encoding="utf-8")

    ld = parse_lyrics_file(f)
    # Should infer title and artist from filename
    assert ld is not None
    assert ld.title == "A Song"
    assert ld.artist == "An Artist"


def test_extract_lyrics_context_basic():
    ld = LyricsData(title="T", artist="A", lyrics="I am so lonely\nI love you baby\nchorus: ooh", is_instrumental=False)
    ctx = extract_lyrics_context(ld)
    assert isinstance(ctx, str)
    assert "The mood" in ctx


def test_match_lyrics_to_catalog(tmp_path: Path):
    # Create fake catalog
    catalog = {
        "songs": [
            {"id": 123, "title": "My Title", "artist": "Some Artist"},
            {"id": 456, "title": "Other Song", "artist": "Another"},
        ]
    }

    # Create lyrics file matching first song
    content = (
        "Title: My Title\n"
        "Artist: Some Artist\n"
        "--------------------------------------------------------------------------------\n"
        "Lyric line here\n"
    )
    f = tmp_path / "My Title by Some Artist.txt"
    f.write_text(content, encoding="utf-8")

    matched = match_lyrics_to_catalog(tmp_path, catalog)
    assert "123" in matched
    assert matched["123"].title == "My Title"


def test_pipeline_loads_lyrics(tmp_path: Path):
    # Backup existing catalog.json if present
    repo_catalog = Path("data/catalog.json")
    backup = None
    if repo_catalog.exists():
        backup = repo_catalog.read_text(encoding='utf-8')

    try:
        # Write a minimal catalog that references id 999
        repo_catalog.parent.mkdir(exist_ok=True)
        cat = {"songs": [{"id": 999, "title": "Unique Song", "artist": "Solo Artist"}]}
        repo_catalog.write_text(json.dumps(cat), encoding='utf-8')

        # Create corresponding lyrics file in tmp_path
        content = (
            "Title: Unique Song\n"
            "Artist: Solo Artist\n"
            "--------------------------------------------------------------------------------\n"
            "Solo lyric line\n"
        )
        f = tmp_path / "Unique Song by Solo Artist.txt"
        f.write_text(content, encoding="utf-8")

        from src.ai_radio.generation.pipeline import GenerationPipeline
        p = GenerationPipeline(lyrics_dir=tmp_path)
        assert "999" in p._lyrics_map
        assert p._lyrics_map["999"].title == "Unique Song"
    finally:
        # Restore original catalog.json
        if backup is not None:
            repo_catalog.write_text(backup, encoding='utf-8')
        else:
            try:
                repo_catalog.unlink()
            except Exception:
                pass


def test_generate_song_intro_passes_lyrics_context(monkeypatch, tmp_path: Path):
    # Prepare a pipeline with prompt_version v2
    from src.ai_radio.generation.pipeline import GenerationPipeline
    p = GenerationPipeline(lyrics_dir=None)
    p.prompt_version = 'v2'

    # Insert a lyrics entry for id 321
    from src.ai_radio.generation.lyrics_parser import LyricsData
    p._lyrics_map['321'] = LyricsData(title='Love Song', artist='Someone', lyrics='I love you baby', is_instrumental=False)

    captured = {}

    def fake_generate_text(client, prompt, banned_phrases=None):
        captured['prompt'] = prompt
        return 'Generated text with lyrics context'

    monkeypatch.setattr('src.ai_radio.generation.llm_client.generate_text', fake_generate_text)

    # Run generation (text_only to avoid tts)
    res = p.generate_song_intro(song_id='321', artist='Someone', title='Love Song', dj='julie', text_only=True)
    assert res.success
    assert 'lyrics context' in captured['prompt'].lower() or 'song theme' in captured['prompt'].lower() or 'i love you' in captured['prompt'].lower()


def test_extract_lyrics_context_on_sample_files():
    from pathlib import Path
    from src.ai_radio.generation.lyrics_parser import parse_lyrics_file, extract_lyrics_context

    lyrics_dir = Path('music_with_lyrics')
    assert lyrics_dir.exists()

    count = 0
    for p in sorted(lyrics_dir.glob('*.txt'))[:10]:
        ld = parse_lyrics_file(p)
        # parsed data should not be None
        assert ld is not None
        ctx = extract_lyrics_context(ld)
        assert isinstance(ctx, str) and ctx
        # Heuristic checks: less than 3 sentences and under 200 chars
        sentences = [s for s in ctx.split('.') if s.strip()]
        assert 1 <= len(sentences) <= 3
        assert len(ctx) <= 200
        count += 1
    assert count == 10
