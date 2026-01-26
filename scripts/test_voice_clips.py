#!/usr/bin/env python3
"""
Voice Clip A/B Testing - Compare different voice reference clips

Tests different Julie voice reference clips to find the best one
for Chatterbox Turbo with baseline parameters.

Clips tested:
- julie_10sec.wav (10s clip)
- julie_30sec.wav (30s clip)
- julie.wav (full ~55s original)
- Julie happy excited v2.wav (~15s energetic)
- Julie semi serious.wav (~10s calm)

Baseline params: exag=0.5, cfg=0.5, temp=0.8
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

# Voice reference clips to test - updated per DJ
def get_voice_clips(dj: str) -> dict:
    """Get voice clips to test for the specified DJ."""
    if dj == "julie":
        return {
            "julie_10sec": "assets/voice_references/Julie/julie_10sec.wav",
            "julie_30sec": "assets/voice_references/Julie/julie_30sec.wav",
            "julie_full": "assets/voice_references/Julie/julie.wav",
            "julie_happy_v2": "assets/voice_references/Julie/Julie happy excited v2.wav",
            "julie_semi_serious": "assets/voice_references/Julie/Julie semi serious.wav",
        }
    else:  # mr_new_vegas
        return {
            "mr_new_vegas_10sec": "assets/voice_references/Mister_New_Vegas/mr_new_vegas_10sec.wav",
            "mr_new_vegas_30sec": "assets/voice_references/Mister_New_Vegas/mr_new_vegas_30sec.wav",
            "mr_new_vegas_full": "assets/voice_references/Mister_New_Vegas/mr_new_vegas.wav",
        }

# Use baseline parameters from previous A/B testing
BASELINE_PARAMS = {
    "exaggeration": 0.5,
    "cfg_weight": 0.5,
    "temperature": 0.8,
}


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
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading Chatterbox (Original) on {device}...")
    
    # Enable CUDA optimizations
    if device == "cuda":
        torch.backends.cudnn.benchmark = True
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
    
    model = ChatterboxTTS.from_pretrained(device=device)
    
    if use_half:
        model.t3.model.half()
        model.s3gen.half()
        print("Using fp16 (half precision)")
    
    return model


def generate_audio(model, text: str, audio_prompt_path: str, params: dict):
    """Generate audio using the model with given parameters."""
    wav = model.generate(
        text=text,
        audio_prompt_path=audio_prompt_path,
        **params
    )
    return wav


def run_voice_clip_test(dj: str = "julie", dry_run: bool = False, use_half: bool = False):
    """Run voice clip comparison test."""
    
    # Get voice clips for this DJ
    VOICE_CLIP_TESTS = get_voice_clips(dj)
    
    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("data") / f"voice_clip_test_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = {
        "timestamp": timestamp,
        "dj": dj,
        "params": BASELINE_PARAMS,
        "voice_clips": VOICE_CLIP_TESTS,
        "tests": []
    }
    
    print("=" * 60)
    print("Voice Clip A/B Testing - Original Model")
    print("=" * 60)
    print(f"Parameters: exag={BASELINE_PARAMS['exaggeration']}, "
          f"cfg={BASELINE_PARAMS['cfg_weight']}, temp={BASELINE_PARAMS['temperature']}")
    
    # Get sample scripts
    scripts = get_sample_scripts(dj)
    print(f"\nSelected {len(scripts)} test scripts:")
    for s in scripts:
        print(f"  - [{s['type']}] {s['name'][:40]}... ({s['length']} chars)")
    
    # Check all voice clips exist
    missing_clips = [name for name, path in VOICE_CLIP_TESTS.items() if not Path(path).exists()]
    if missing_clips:
        print(f"\nERROR: Missing voice clips: {', '.join(missing_clips)}")
        return
    
    print(f"\nTesting {len(VOICE_CLIP_TESTS)} voice clips:")
    for name, path in VOICE_CLIP_TESTS.items():
        size = Path(path).stat().st_size
        est_duration = round(size / 32000, 1)
        print(f"  - {name}: {path} (~{est_duration}s)")
    
    if dry_run:
        print(f"\n[DRY RUN] Would generate {len(scripts)} × {len(VOICE_CLIP_TESTS)} = {len(scripts)*len(VOICE_CLIP_TESTS)} audio files")
        return
    
    # Load model
    print("\n" + "="*60)
    model = load_chatterbox_original(use_half=use_half)
    print("="*60)
    
    # Test each script with each voice clip
    for i, script in enumerate(scripts, 1):
        script_name = f"{script['type']}_{script['name'][:30]}"
        script_dir = output_dir / script_name.replace(" ", "_")
        script_dir.mkdir(exist_ok=True)
        
        # Save the text for reference
        (script_dir / "text.txt").write_text(script["text"], encoding="utf-8")
        
        print(f"\n[{i}/{len(scripts)}] {script_name}")
        print(f"  Text: {script['text'][:60]}...")
        
        for clip_name, clip_path in VOICE_CLIP_TESTS.items():
            output_file = script_dir / f"{clip_name}.wav"
            
            # Get clip duration for display
            clip_size = Path(clip_path).stat().st_size
            est_duration = round(clip_size / 32000, 1)
            
            print(f"  Testing {clip_name} (~{est_duration}s)...")
            
            try:
                wav = generate_audio(model, script["text"], clip_path, BASELINE_PARAMS)
                torchaudio.save(str(output_file), wav, model.sr)
                print(f"    ✓ Saved: {output_file.name}")
                
                results["tests"].append({
                    "script": script_name,
                    "voice_clip": clip_name,
                    "clip_path": clip_path,
                    "clip_duration": est_duration,
                    "file": str(output_file),
                    "text_length": len(script["text"]),
                })
            except Exception as e:
                print(f"    ✗ Failed: {e}")
    
    # Save manifest
    manifest_file = output_dir / "manifest.json"
    manifest_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    
    # Print summary
    print("\n" + "="*60)
    print("Voice Clip Test Complete!")
    print("="*60)
    print(f"Output directory: {output_dir}")
    print(f"Manifest: {manifest_file}")
    print(f"\nTotal tests: {len(results['tests'])}")
    
    print("\n" + "="*60)
    print("LISTENING GUIDE")
    print("="*60)
    print("""
For each script, compare the voice clips:

1. julie_10sec (~10s)
   - Short clip from original
   
2. julie_30sec (~30s)
   - Longer clip from original
   
3. julie_full (~55s)
   - Full original clip
   
4. julie_happy_v2 (~15s)
   - Energetic/upbeat segment
   
5. julie_semi_serious (~10s)
   - Calm/sincere segment

Listen for:
- Speech pacing (too fast/slow)
- Voice quality and clarity
- Warbling or artifacts
- Energy level (appropriate for content)
- Overall naturalness
""")
    
    return output_dir


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test different voice reference clips")
    parser.add_argument("--dj", default="julie", help="Which DJ to test")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be generated without running TTS")
    parser.add_argument("--fp16", action="store_true",
                        help="Use half precision (fp16) for faster generation")
    args = parser.parse_args()
    
    run_voice_clip_test(dj=args.dj, dry_run=args.dry_run, use_half=args.fp16)
