import json
from pathlib import Path
import shutil
import pytest

from scripts import generate_with_audit as gwa


class FakeGenerationPipeline:
    """Fake pipeline that can simulate failures on first generation and succeed on retries."""

    def __init__(self, output_dir: Path, fail_first_n: int = 3):
        self.output_dir = output_dir
        self.calls = {}
        self.fail_first_n = fail_first_n

    def _write_script(self, song_id: str, artist: str, title: str, dj: str, content: str):
        safe_artist = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in artist).strip().replace(' ', '_')
        safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in title).strip().replace(' ', '_')
        folder = self.output_dir / "intros" / dj / f"{safe_artist}-{safe_title}"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / f"{dj}_0.txt").write_text(content, encoding='utf-8')

    def generate_song_intro(self, song_id: str, artist: str, title: str, dj: str, text_only: bool = True, **kwargs):
        key = f"{song_id}_{dj}"
        self.calls.setdefault(key, 0)
        self.calls[key] += 1
        # Simulate failures on first call (for a subset)
        if self.calls[key] <= self.fail_first_n:
            content = f"This is a borderline intro for {artist} - {title} borderline"
            self._write_script(song_id, artist, title, dj, content)
            return type('R', (), {'success': True, 'text': content})
        else:
            content = f"Good intro for {artist} - {title} This sounds great"
            self._write_script(song_id, artist, title, dj, content)
            return type('R', (), {'success': True, 'text': content})


@pytest.mark.mock
def test_checkpoint_6_1_intro_baseline_mock(tmp_path):
    # Prepare temporary DATA and GENERATED dirs
    tmp_data = tmp_path / "data"
    tmp_generated = tmp_data / "generated"

    # Monkeypatch global dirs in generate_with_audit
    gwa.DATA_DIR = tmp_data
    gwa.GENERATED_DIR = tmp_generated

    # Ensure clean state
    if tmp_data.exists():
        shutil.rmtree(tmp_data)

    tmp_data.mkdir(parents=True)

    # Create a fake catalog.json used by the pipeline loader
    catalog = {"songs": []}
    for i in range(10):
        catalog["songs"].append({"id": i, "artist": f"Artist {i}", "title": f"Title {i}"})
    (tmp_data / "catalog.json").write_text(json.dumps(catalog), encoding='utf-8')

    songs = gwa.load_catalog_songs(tmp_data / "catalog.json", limit=10)

    checkpoint_file = tmp_data / "pipeline_state.json"
    checkpoint = gwa.PipelineCheckpoint(checkpoint_file)

    # Use FakeGenerationPipeline that fails first 2 attempts per script
    pipeline = FakeGenerationPipeline(output_dir=tmp_generated, fail_first_n=2)

    # Stage 1: generate
    generated = gwa.stage_generate(pipeline, songs, ["julie"], checkpoint, test_mode=True)
    assert generated == 10

    # Stage 2: audit (initial)
    stats_initial = gwa.stage_audit(songs, ["julie"], checkpoint, test_mode=True)
    total = stats_initial['passed'] + stats_initial['failed']
    assert total == 10
    initial_pass_rate = stats_initial['passed'] / total
    assert initial_pass_rate >= 0.0  # May be variable; ensure audit happened

    # Regenerate failed scripts
    regenerated = gwa.stage_regenerate(pipeline, songs, ["julie"], max_retries=5, test_mode=True)
    # After regeneration, compute final pass/fail from audit files
    passed = len(list((tmp_data / "audit" / "julie" / "passed").glob("*.json")))
    failed = len(list((tmp_data / "audit" / "julie" / "failed").glob("*.json")))

    final_total = passed + failed
    assert final_total == 10
    final_pass_rate = passed / final_total

    assert final_pass_rate >= 0.95
