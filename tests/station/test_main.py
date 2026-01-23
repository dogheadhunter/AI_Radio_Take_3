import pytest
from unittest.mock import patch
from src.ai_radio.main import parse_args, main


class TestParseArgs:
    def test_dry_run_flag(self):
        with patch('sys.argv', ['main', '--dry-run']):
            args = parse_args()
            assert args.dry_run is True

    def test_no_weather_flag(self):
        with patch('sys.argv', ['main', '--no-weather']):
            args = parse_args()
            assert args.no_weather is True

    def test_defaults(self):
        with patch('sys.argv', ['main']):
            args = parse_args()
            assert args.dry_run is False
            assert args.no_weather is False
            assert args.no_shows is False


class DummyPath:
    def __init__(self, exists=True):
        self._exists = exists

    def exists(self):
        return self._exists


def test_dry_run_exits_zero(monkeypatch):
    with patch('sys.argv', ['main', '--dry-run']):
        result = main()
        assert result == 0


def test_missing_catalog_exits_one(monkeypatch):
    # Monkeypatch CATALOG_FILE in main.py's namespace (where it's imported)
    monkeypatch.setattr('src.ai_radio.main.CATALOG_FILE', DummyPath(False))
    with patch('sys.argv', ['main']):
        result = main()
        assert result == 1
