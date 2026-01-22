"""Tests for scripts/validate_setup.py."""
import subprocess
from types import SimpleNamespace
from pathlib import Path
import sys

import scripts.validate_setup as vs


def test_check_python_version():
    assert vs.check_python_version() is True


def test_check_import_success():
    assert vs.check_import("pytest") is True


def test_check_import_failure(monkeypatch):
    # Simulate ImportError for fakepkg
    original_import = __import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "fakepkg":
            raise ImportError("nope")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", fake_import)
    assert vs.check_import("fakepkg") is False


def test_check_ollama_success(monkeypatch):
    res = SimpleNamespace(returncode=0, stdout="ok", stderr="")

    def fake_run(cmd, capture_output, text, timeout):
        return res

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert vs.check_ollama() is True


def test_check_ollama_missing(monkeypatch):
    def fake_run(cmd, capture_output, text, timeout):
        raise FileNotFoundError()

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert vs.check_ollama() is False


def test_check_directory_structure(tmp_path, monkeypatch):
    # create the required dirs under a temporary project root and point the script there
    project_root = tmp_path
    (project_root / "src" / "ai_radio").mkdir(parents=True)
    (project_root / "tests").mkdir()
    (project_root / "data").mkdir()
    (project_root / "logs").mkdir()
    (project_root / "assets").mkdir()

    monkeypatch.setattr(vs, "__file__", str(project_root / "scripts" / "validate_setup.py"))

    assert vs.check_directory_structure() is True


def test_check_config_import():
    # Importing ai_radio.config should work in this repo
    assert vs.check_config_import() is True


def test_main_all_ok(monkeypatch, tmp_path, capsys):
    # Arrange: make imports succeed and ollama succeed, create dirs
    (tmp_path / "src" / "ai_radio").mkdir(parents=True)
    (tmp_path / "tests").mkdir()
    (tmp_path / "data").mkdir()
    (tmp_path / "logs").mkdir()
    (tmp_path / "assets").mkdir()

    monkeypatch.setattr(vs, "__file__", str(tmp_path / "scripts" / "validate_setup.py"))

    # fake subprocess.run
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=0))

    # Ensure mutagen import succeeds by temporarily inserting dummy module
    sys.modules.setdefault("mutagen", SimpleNamespace())

    rv = vs.main()
    captured = capsys.readouterr()
    assert rv == 0
    assert "All checks passed" in captured.out
