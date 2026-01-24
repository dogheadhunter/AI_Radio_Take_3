import re
from src.ai_radio.generation.prompts_v2 import (
    build_song_intro_prompt_v2,
    build_song_outro_prompt_v2,
    build_time_prompt_v2,
    build_weather_prompt_v2,
    FORBIDDEN_WORDS,
    JULIE_EXAMPLES,
    MR_NV_EXAMPLES,
)
from src.ai_radio.generation.prompts import DJ
from src.ai_radio.generation.pipeline import GenerationPipeline


def test_build_song_intro_prompt_v2_structure():
    p = build_song_intro_prompt_v2(DJ.JULIE, artist="Nat King Cole", title="Mona Lisa", year=1950)
    assert isinstance(p, dict)
    assert "system" in p and "user" in p
    assert "Forbidden elements" in p["system"] or "DO NOT INCLUDE" in p["system"]


def test_forbidden_words_mentioned_in_system():
    p = build_song_intro_prompt_v2(DJ.MR_NEW_VEGAS, artist="Frank", title="Blue Moon")
    sys = p["system"].lower()
    # At least one forbidden word should be explicitly listed
    assert any(w.lower() in sys for w in FORBIDDEN_WORDS)


def test_pipeline_uses_v2_prompts(monkeypatch, tmp_path):
    captured = {}

    def fake_generate_text(llm, prompt):
        # capture the prompt and return a stubbed text
        captured['prompt'] = prompt
        return "STUBBED PROMPT OUTPUT"

    # Patch the reference used by pipeline (pipeline imports generate_text into its module namespace)
    monkeypatch.setattr('src.ai_radio.generation.pipeline.generate_text', fake_generate_text)

    pipeline = GenerationPipeline(output_dir=tmp_path, prompt_version='v2')
    res = pipeline.generate_song_intro(song_id='s1', artist='Ella Fitzgerald', title='Dream a Little Dream', dj='julie', text_only=True)

    assert res.success
    assert 'prompt' in captured
    prompt_text = captured['prompt']
    # Ensure few-shot example or role text is present in the final prompt string
    assert any(ex in prompt_text for ex in JULIE_EXAMPLES)
    # Ensure forbidden list was included
    assert any(fw in prompt_text.lower() for fw in [w.lower() for w in FORBIDDEN_WORDS])


def test_content_type_prompts_return_structure_and_constraints():
    # Outro
    out = build_song_outro_prompt_v2(DJ.JULIE, artist="Billie Holiday", title="God Bless the Child", next_song="Someone To Watch Over Me")
    assert isinstance(out, dict) and "system" in out and "user" in out
    assert "Length" in out["user"] or "Length:" in out["user"] or "1-2 sentences" in out["user"]

    # Time
    time_p = build_time_prompt_v2(DJ.MR_NEW_VEGAS, hour=9, minute=0)
    assert isinstance(time_p, dict) and "system" in time_p and "user" in time_p
    assert "Length" in time_p["user"] or "one sentence" in time_p["user"]

    # Weather
    weather_p = build_weather_prompt_v2(DJ.JULIE, "Sunny and mild", hour=6)
    assert isinstance(weather_p, dict) and "system" in weather_p and "user" in weather_p
    assert "2-3 sentence" in weather_p["user"] or "2-3" in weather_p["user"] or "2-3 sentence" in weather_p["system"]


def test_default_pipeline_uses_v1(monkeypatch, tmp_path):
    captured = {}

    def fake_generate_text(llm, prompt):
        captured['prompt'] = prompt
        return "DEFAULT-STUB"

    monkeypatch.setattr('src.ai_radio.generation.pipeline.generate_text', fake_generate_text)

    pipeline = GenerationPipeline(output_dir=tmp_path)
    res = pipeline.generate_song_intro(song_id='s2', artist='Billie', title='Autumn in New York', dj='julie', text_only=True)
    assert res.success
    assert 'prompt' in captured
    prompt_text = captured['prompt']
    # v1 prompts should NOT include the v2 few-shot examples
    assert not any(ex in prompt_text for ex in JULIE_EXAMPLES)
