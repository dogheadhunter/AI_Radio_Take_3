from pathlib import Path
from src.ai_radio.dj.content import ContentSelector, get_outro_for_song, mark_outro_used


class TestOutroSelection:
    def test_returns_path_to_outro(self, content_with_intros):
        selector = ContentSelector(content_dir=content_with_intros)
        outro = get_outro_for_song(selector, song_id="song_1", dj="julie")
        assert isinstance(outro, Path)
        assert outro.exists()

    def test_returns_none_if_no_outro(self, empty_content_dir):
        selector = ContentSelector(content_dir=empty_content_dir)
        outro = get_outro_for_song(selector, song_id="nonexistent", dj="julie")
        assert outro is None

    def test_selects_correct_dj_outro(self, content_with_intros):
        selector = ContentSelector(content_dir=content_with_intros)
        julie_outro = get_outro_for_song(selector, song_id="song_1", dj="julie")
        vegas_outro = get_outro_for_song(selector, song_id="song_1", dj="mr_new_vegas")
        assert "julie" in str(julie_outro).lower()
        assert "vegas" in str(vegas_outro).lower() or "mr_new" in str(vegas_outro).lower()

    def test_mark_outro_used_and_rotation(self, content_with_multiple_intros):
        selector = ContentSelector(content_dir=content_with_multiple_intros)
        # create multiple outros in the temp dir
        for i in range(3):
            (selector.content_dir / f"julie_song_1_outro_{i}.mp3").write_text("x")

        outros = []
        for _ in range(6):
            outro = get_outro_for_song(selector, song_id="song_1", dj="julie")
            mark_outro_used(selector, outro)
            outros.append(str(outro))

        # Should see some variety
        assert len(set(outros)) > 1
