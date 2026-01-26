#!/usr/bin/env python3
"""
Model Comparison: Chatterbox Original vs Turbo

Compares the original Chatterbox model against Chatterbox Turbo
using the optimal baseline parameters from A/B testing.

Baseline params:
- exaggeration: 0.5
- cfg_weight: 0.5
- temperature: 0.8
"""

import os
import sys
import json
import random
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
import torchaudio

# Optimal parameters from A/B testing
BASELINE_PARAMS = {
    "exaggeration": 0.5,
    "cfg_weight": 0.5,
    "temperature": 0.8,
}

# Voice reference
VOICE_REF = "assets/voice_references/Julie/julie_10sec.wav"

def get_sample_scripts(dj: str, count: int = 10) -> list[dict]:
    """Get a diverse sample of scripts for testing."""
    scripts = []
    base_path = Path("data/generated")
    
    # Get intros (variety of song types)
    intros_path = base_path / "intros" / dj
    if intros_path.exists():
        intro_dirs = list(intros_path.iterdir())
        sample_dirs = random.sample(intro_dirs, min(6, len(intro_dirs)))
        for d in sample_dirs:
            txt_files = list(d.glob("*.txt"))
            if txt_files:
                content = txt_files[0].read_text(encoding="utf-8")
                scripts.append({
                    "type": "intro",
                    "name": d.name,
                    "text": content,
                    "length": len(content)
                })
    
    # Get time announcements (2 samples)
    time_path = base_path / "time" / dj
    if time_path.exists():
        time_dirs = list(time_path.iterdir())
        if time_dirs:
            sample_time_dirs = random.sample(time_dirs, min(2, len(time_dirs)))
            for sample_dir in sample_time_dirs:
                txt_files = list(sample_dir.glob("*.txt"))
                if txt_files:
                    content = txt_files[0].read_text(encoding="utf-8")
                    scripts.append({
                        "type": "time",
                        "name": sample_dir.name,
                        "text": content,
                        "length": len(content)
                    })
    
    # Get weather announcements (2 samples)
    weather_path = base_path / "weather" / dj
    if weather_path.exists():
        weather_dirs = list(weather_path.iterdir())
        if weather_dirs:
            sample_weather_dirs = random.sample(weather_dirs, min(2, len(weather_dirs)))
            for sample_dir in sample_weather_dirs:
                txt_files = list(sample_dir.glob("*.txt"))
                if txt_files:
                    content = txt_files[0].read_text(encoding="utf-8")
                    scripts.append({
                        "type": "weather",
                        "name": sample_dir.name,
                        "text": content,
                        "length": len(content)
                    })
    
    return scripts[:count]


def load_chatterbox_original(use_half: bool = False):
    """Load the original Chatterbox TTS model."""
    # Add chatterbox src to path
    chatterbox_path = Path(__file__).parent.parent / "chatterbox" / "src"
    if str(chatterbox_path) not in sys.path:
        sys.path.insert(0, str(chatterbox_path))
    
    from chatterbox.tts import ChatterboxTTS
    
    print("Loading Chatterbox (Original) on cuda...")
    model = ChatterboxTTS.from_pretrained(device="cuda")
    
    if use_half:
        model.t3.model.half()
        model.s3gen.half()
        print("Using fp16 (half precision)")
    
    # Enable CUDA optimizations
    torch.backends.cudnn.benchmark = True
    torch.backends.cuda.matmul.allow_tf32 = True
    
    return model


def load_chatterbox_turbo(use_half: bool = False):
    """Load the Chatterbox Turbo TTS model."""
    # Add chatterbox src to path
    chatterbox_path = Path(__file__).parent.parent / "chatterbox" / "src"
    if str(chatterbox_path) not in sys.path:
        sys.path.insert(0, str(chatterbox_path))
    
    from chatterbox.tts_turbo import ChatterboxTurboTTS
    
    print("Loading Chatterbox Turbo on cuda...")
    model = ChatterboxTurboTTS.from_pretrained(device="cuda")
    
    if use_half:
        model.t3.model.half()
        model.s3gen.half()
        print("Using fp16 (half precision)")
    
    # Enable CUDA optimizations
    torch.backends.cudnn.benchmark = True
    torch.backends.cuda.matmul.allow_tf32 = True
    
    return model


def generate_audio(model, text: str, audio_prompt_path: str, params: dict):
    """Generate audio using the model with given parameters."""
    wav = model.generate(
        text=text,
        audio_prompt_path=audio_prompt_path,
        **params
    )
    return wav


def run_model_comparison(dj: str = "julie", dry_run: bool = False, use_half: bool = False):
    """Run model comparison test."""
    
    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("data") / f"model_comparison_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = {
        "timestamp": timestamp,
        "dj": dj,
        "voice_ref": VOICE_REF,
        "params": BASELINE_PARAMS,
        "tests": []
    }
    
    print("=" * 60)
    print("Model Comparison: Original vs Turbo")
    print("=" * 60)
    print(f"Parameters: exag={BASELINE_PARAMS['exaggeration']}, "
          f"cfg={BASELINE_PARAMS['cfg_weight']}, temp={BASELINE_PARAMS['temperature']}")
    print(f"Voice ref: {VOICE_REF}")
    
    # Get sample scripts
    scripts = get_sample_scripts(dj)
    print(f"\nSelected {len(scripts)} test scripts:")
    for s in scripts:
        print(f"  - [{s['type']}] {s['name'][:40]}... ({s['length']} chars)")
    
    # Check voice reference
    if not Path(VOICE_REF).exists():
        print(f"ERROR: Voice reference not found: {VOICE_REF}")
        return
    
    if dry_run:
        print(f"\n[DRY RUN] Would generate {len(scripts)} × 2 models = {len(scripts)*2} audio files")
        return
    
    # Load original model and generate all scripts
    print("\n" + "="*60)
    model_original = load_chatterbox_original(use_half=use_half)
    print("="*60)
    
    print("\n" + "="*60)
    print("PHASE 1: Generating with Original Model")
    print("="*60)
    
    for i, script in enumerate(scripts, 1):
        script_name = f"{script['type']}_{script['name'][:30]}"
        script_dir = output_dir / script_name.replace(" ", "_")
        script_dir.mkdir(exist_ok=True)
        
        # Save the text for reference
        (script_dir / "text.txt").write_text(script["text"], encoding="utf-8")
        
        print(f"\n[{i}/{len(scripts)}] {script_name}")
        print(f"  Text: {script['text'][:60]}...")
        
        try:
            import time
            start = time.time()
            wav = generate_audio(model_original, script["text"], VOICE_REF, BASELINE_PARAMS)
            duration = time.time() - start
            
            output_file = script_dir / "original.wav"
            torchaudio.save(str(output_file), wav, model_original.sr)
            print(f"  ✓ Saved in {duration:.1f}s")
            
            results["tests"].append({
                "script": script_name,
                "model": "original",
                "file": str(output_file),
                "generation_time": duration,
                "text_length": len(script["text"]),
            })
        except Exception as e:
            print(f"  ✗ Failed: {e}")
    
    # Unload original model
    print("\n" + "="*60)
    print("Unloading Original model...")
    del model_original
    torch.cuda.empty_cache()
    print("="*60)
    
    # Load turbo model and generate all scripts
    print("\n" + "="*60)
    model_turbo = load_chatterbox_turbo(use_half=use_half)
    print("="*60)
    
    print("\n" + "="*60)
    print("PHASE 2: Generating with Turbo Model")
    print("="*60)
    
    for i, script in enumerate(scripts, 1):
        script_name = f"{script['type']}_{script['name'][:30]}"
        script_dir = output_dir / script_name.replace(" ", "_")
        
        print(f"\n[{i}/{len(scripts)}] {script_name}")
        
        try:
            import time
            start = time.time()
            wav = generate_audio(model_turbo, script["text"], VOICE_REF, BASELINE_PARAMS)
            duration = time.time() - start
            
            output_file = script_dir / "turbo.wav"
            torchaudio.save(str(output_file), wav, model_turbo.sr)
            print(f"  ✓ Saved in {duration:.1f}s")
            
            results["tests"].append({
                "script": script_name,
                "model": "turbo",
                "file": str(output_file),
                "generation_time": duration,
                "text_length": len(script["text"]),
            })
        except Exception as e:
            print(f"  ✗ Failed: {e}")
    
    # Unload turbo model
    print("\n" + "="*60)
    print("Unloading Turbo model...")
    del model_turbo
    torch.cuda.empty_cache()
    print("="*60)
    
    # Save manifest
    manifest_file = output_dir / "manifest.json"
    manifest_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    
    # Print summary
    print("\n" + "="*60)
    print("Comparison Complete!")
    print("="*60)
    print(f"Output directory: {output_dir}")
    print(f"Manifest: {manifest_file}")
    
    # Calculate average generation times
    original_times = [t["generation_time"] for t in results["tests"] if t["model"] == "original"]
    turbo_times = [t["generation_time"] for t in results["tests"] if t["model"] == "turbo"]
    
    if original_times and turbo_times:
        avg_original = sum(original_times) / len(original_times)
        avg_turbo = sum(turbo_times) / len(turbo_times)
        speedup = avg_original / avg_turbo if avg_turbo > 0 else 0
        
        print(f"\nAverage generation time:")
        print(f"  Original: {avg_original:.1f}s")
        print(f"  Turbo:    {avg_turbo:.1f}s")
        print(f"  Speedup:  {speedup:.2f}x")
    
    print("\n" + "="*60)
    print("LISTENING GUIDE")
    print("="*60)
    print("""
For each script, compare:

1. ORIGINAL
   - Higher quality (potentially)
   - Slower generation

2. TURBO
   - Faster generation
   - Quality trade-off?

Listen for:
- Audio quality differences
- Prosody and pacing
- Clarity and naturalness
- Artifacts or warbling
""")
    
    return output_dir


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Compare Chatterbox Original vs Turbo")
    parser.add_argument("--dj", default="julie", help="Which DJ to test")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be generated without running TTS")
    parser.add_argument("--fp16", action="store_true",
                        help="Use half precision (fp16) for faster generation")
    args = parser.parse_args()
    
    run_model_comparison(dj=args.dj, dry_run=args.dry_run, use_half=args.fp16)
