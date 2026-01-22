import os
from ai_radio.config import Config
from ai_radio.exceptions import ConfigError
from src.ai_radio.config import MUSIC_DIR_ENV, LOG_LEVEL_ENV


def test_from_env_defaults(monkeypatch):
    monkeypatch.delenv(MUSIC_DIR_ENV, raising=False)
    monkeypatch.setenv(LOG_LEVEL_ENV, "DEBUG")

    cfg = Config.from_env()
    assert cfg.log_level == "DEBUG"
    assert cfg.music_dir is None


def test_validate_missing_music_dir():
    cfg = Config(music_dir=None)
    try:
        cfg.validate()
        assert False, "expected ConfigError"
    except ConfigError as exc:
        assert f"{MUSIC_DIR_ENV} is not set" in str(exc)


def test_validate_music_dir_not_dir(tmp_path):
    # create a file (not dir)
    f = tmp_path / "not_a_dir"
    f.write_text("nope")

    cfg = Config(music_dir=str(f))
    try:
        cfg.validate()
        assert False, "expected ConfigError"
    except ConfigError as exc:
        assert "does not point to a directory" in str(exc)


def test_validate_music_dir_ok(tmp_path, monkeypatch):
    d = tmp_path / "music"
    d.mkdir()
    monkeypatch.setenv(MUSIC_DIR_ENV, str(d))

    cfg = Config.from_env()
    cfg.validate()
    assert cfg.music_dir == str(d)
