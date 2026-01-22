from pathlib import Path
from src.ai_radio.dj.content import ContentSelector, get_intro_for_song, get_time_announcement, mark_intro_used


class TestIntroSelection:
    def test_returns_path_to_audio(self, content_with_intros):
        selector = ContentSelector(content_dir=content_with_intros)
        intro = get_intro_for_song(selector, song_id="song_1", dj="julie")
        assert isinstance(intro, Path)
        assert intro.exists()

    def test_returns_none_if_no_intro(self, empty_content_dir):
        selector = ContentSelector(content_dir=empty_content_dir)
        intro = get_intro_for_song(selector, song_id="nonexistent", dj="julie")
        assert intro is None

    def test_selects_different_intro_each_time(self, content_with_multiple_intros):
        selector = ContentSelector(content_dir=content_with_multiple_intros)
        intros = []
        for _ in range(10):
            intro = get_intro_for_song(selector, song_id="song_1", dj="julie")
            mark_intro_used(selector, intro)
            intros.append(str(intro))

        unique_intros = set(intros)
        assert len(unique_intros) > 1

    def test_selects_correct_dj_intro(self, content_with_intros):
        selector = ContentSelector(content_dir=content_with_intros)
        julie_intro = get_intro_for_song(selector, song_id="song_1", dj="julie")
        vegas_intro = get_intro_for_song(selector, song_id="song_1", dj="mr_new_vegas")
        assert "julie" in str(julie_intro).lower()
        assert "vegas" in str(vegas_intro).lower() or "mr_new" in str(vegas_intro).lower()


class TestTimeAnnouncements:
    def test_returns_audio_path(self, content_with_intros):
        selector = ContentSelector(content_dir=content_with_intros)
        from datetime import datetime
        announcement = get_time_announcement(selector, dj="julie", time=datetime(2026, 1, 22, 14, 30))
        assert isinstance(announcement, Path)

    def test_different_for_different_times(self, content_with_intros):
        selector = ContentSelector(content_dir=content_with_intros)
        from datetime import datetime
        two_pm = get_time_announcement(selector, "julie", datetime(2026, 1, 22, 14, 0))
        three_pm = get_time_announcement(selector, "julie", datetime(2026, 1, 22, 15, 0))
        # They may be None if not available, but if available they should differ for different hours
        if two_pm and three_pm:
            assert two_pm != three_pm
