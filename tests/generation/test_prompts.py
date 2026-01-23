"""Tests for prompt templates."""
import pytest
from src.ai_radio.generation.prompts import build_song_intro_prompt, build_time_announcement_prompt, build_weather_prompt, build_song_outro_prompt, DJ


def test_includes_song_title_and_artist():
    prompt = build_song_intro_prompt(DJ.JULIE, artist="Bing Crosby", title="White Christmas", year=1942)
    assert "White Christmas" in prompt
    assert "Bing Crosby" in prompt


def test_julie_prompt_has_julie_traits():
    prompt = build_song_intro_prompt(DJ.JULIE, artist="Test", title="Test")
    assert "friendly" in prompt.lower() or "earnest" in prompt.lower()


def test_mr_vegas_prompt_has_his_traits():
    prompt = build_song_intro_prompt(DJ.MR_NEW_VEGAS, artist="Test", title="Test")
    assert "suave" in prompt.lower() or "romantic" in prompt.lower()


def test_different_djs_produce_different_prompts():
    julie_prompt = build_song_intro_prompt(DJ.JULIE, "Test", "Test")
    vegas_prompt = build_song_intro_prompt(DJ.MR_NEW_VEGAS, "Test", "Test")
    assert julie_prompt != vegas_prompt


def test_time_prompt_includes_formatted_time():
    prompt = build_time_announcement_prompt(14, 30, DJ.JULIE)
    assert "2:30" in prompt or "2:30 PM" in prompt


def test_outro_prompt_is_short_and_personalized():
    prompt = build_song_outro_prompt(DJ.MR_NEW_VEGAS, "Frank Sinatra", "My Way", next_song="New Song")
    assert "My Way" in prompt
    assert "New Song" in prompt
    assert len(prompt) < 300  # short prompt for an outro
