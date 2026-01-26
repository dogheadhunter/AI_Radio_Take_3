#!/usr/bin/env python3
"""
A/B Testing Script for Chatterbox TTS Parameters

Tests different combinations of:
- exaggeration: 0.4, 0.5, 0.6
- cfg_weight: 0.3, 0.35, 0.4
- temperature: 0.7, 0.8, 0.9

For both Julie and Mr. New Vegas DJs.
"""

import os
import sys
import json
import random
from pathlib import Path
from datetime import datetime
from itertools import product

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
import torchaudio

# Voice reference clips to test
VOICE_CLIP_TESTS = {
    "julie_10sec": "assets/voice_references/Julie/julie_10sec.wav",
    "julie_30sec": "assets/voice_references/Julie/julie_30sec.wav",
    "julie_full": "assets/voice_references/Julie/julie.wav",
    "julie_happy_v2": "assets/voice_references/Julie/Julie happy excited v2.wav",
    "julie_semi_serious": "assets/voice_references/Julie/Julie semi serious.wav",
}

# Use baseline parameters from A/B testing for all clips
BASELINE_PARAMS = {
    "exaggeration": 0.5,
    "cfg_weight": 0.5,
    "temperature": 0.8,
}

def detect_mood(text: str) -> str:
    """Detect if script text suggests a sad/melancholic or energetic/happy song."""
    text_lower = text.lower()
    
    # Keywords suggesting sad/melancholic mood
    sad_keywords = [
        "sad", "melancholy", "heartbreak", "lonely", "lonesome", "crying",
        "tears", "loss", "miss", "missing", "bittersweet", "somber", "wistful",
        "regret", "sorrow", "blues", "haunting", "mournful", "tender",
        "gentle", "quiet", "peaceful", "reflective", "nostalgic"
    ]
    
    # Keywords suggesting energetic/happy mood
    energetic_keywords = [
        "fun", "happy", "upbeat", "swing", "dance", "dancing", "jumping",
        "party", "celebrate", "energetic", "lively", "bouncy", "catchy",
        "groovy", "jazzy", "peppy", "cheerful", "joyful", "exciting",
        "wild", "crazy", "rock", "boogie", "hot"
    ]
    
    sad_score = sum(1 for kw in sad_keywords if kw in text_lower)
    energetic_score = sum(1 for kw in energetic_keywords if kw in text_lower)
    
    if sad_score > energetic_score:
        return "calm"
    return "energetic"


def get_voice_ref(dj: str, content_type: str, script_text: str = "") -> str:
    """Get appropriate voice reference based on content type and script mood."""
    refs = VOICE_REFS.get(dj, {})
    
    # For intros/outros, detect mood from script text
    if content_type in ("intro", "outro") and script_text:
        preferred = detect_mood(script_text)
    else:
        # Map other content types to energy levels
        energy_map = {
            "time": "calm",
            "weather": "calm",
        }
        preferred = energy_map.get(content_type, "default")
    
    # Fall back to default if specific energy version doesn't exist
    if preferred in refs and Path(refs[preferred]).exists():
        return refs[preferred]
    return refs.get("default", "")

def get_sample_scripts(dj: str, count: int = 10) -> list[dict]:
    """Get a diverse sample of scripts for testing."""
    scripts = []
    base_path = Path("data/generated")
    
    # Get intros (variety of song types)
    intros_path = base_path / "intros" / dj
    if intros_path.exists():
        intro_dirs = list(intros_path.iterdir())
        # Pick diverse samples - short names, long names, different artists
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


def load_chatterbox(use_half: bool = False):
    """Load the Chatterbox Turbo TTS model with optional fp16 for faster generation."""
    # Add chatterbox src to path
    chatterbox_path = Path(__file__).parent.parent / "chatterbox" / "src"
    if str(chatterbox_path) not in sys.path:
        sys.path.insert(0, str(chatterbox_path))
    
    from chatterbox.tts_turbo import ChatterboxTurboTTS
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading Chatterbox Turbo on {device}...")
    
    # Enable CUDA optimizations
    if device == "cuda":
        torch.backends.cudnn.benchmark = True
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
    
    model = ChatterboxTurboTTS.from_pretrained(device=device)
    
    # Convert to half precision for faster inference (CUDA only)
    if use_half and device == "cuda":
        print("Using fp16 (half precision) for faster generation...")
        model.t3 = model.t3.half()
        model.s3gen = model.s3gen.half()
        model.ve = model.ve.half()
    
    return model


def generate_audio(model, text: str, voice_ref: str, params: dict) -> torch.Tensor:
    """Generate audio with specific parameters."""
    with torch.amp.autocast('cuda', enabled=torch.cuda.is_available()):
        wav = model.generate(
            text=text,
            audio_prompt_path=voice_ref,
            exaggeration=params["exaggeration"],
            cfg_weight=params["cfg_weight"],
            temperature=params["temperature"],
        )
    return wav


def run_ab_test(djs: list[str] = None, dry_run: bool = False, use_half: bool = True):
    """Run the A/B test for all parameter combinations."""
    if djs is None:
        djs = ["julie", "mr_new_vegas"]
    
    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f"data/ab_test_{timestamp}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = {
        "timestamp": timestamp,
        "param_sets": PARAM_SETS,
        "tests": []
    }
    
    print("=" * 60)
    print("TTS A/B Testing - Parameter Optimization")
    print("=" * 60)
    
    # Load model (unless dry run)
    model = None if dry_run else load_chatterbox(use_half=use_half)
    
    for dj in djs:
        print(f"\n{'='*40}")
        print(f"Testing DJ: {dj.upper()}")
        print(f"{'='*40}")
        
        # Get sample scripts
        scripts = get_sample_scripts(dj)
        print(f"Selected {len(scripts)} test scripts:")
        for s in scripts:
            print(f"  - [{s['type']}] {s['name'][:40]}... ({s['length']} chars)")
        
        # Check default voice reference exists
        default_ref = get_voice_ref(dj, "intro", "test")
        if not Path(default_ref).exists():
            print(f"WARNING: Voice reference not found: {default_ref}")
            print("Skipping this DJ...")
            continue
        
        # Create DJ output folder
        dj_dir = output_dir / dj
        dj_dir.mkdir(exist_ok=True)
        
        # Test each script with each parameter set
        for script in scripts:
            script_name = f"{script['type']}_{script['name'][:30]}"
            script_dir = dj_dir / script_name.replace(" ", "_")
            script_dir.mkdir(exist_ok=True)
            
            # Get voice reference appropriate for this content type and mood
            voice_ref = get_voice_ref(dj, script["type"], script["text"])
            mood = detect_mood(script["text"]) if script["type"] in ("intro", "outro") else "n/a"
            
            # Save the text for reference
            (script_dir / "text.txt").write_text(script["text"], encoding="utf-8")
            
            print(f"\n  Script: {script_name}")
            print(f"  Mood: {mood} | Voice ref: {Path(voice_ref).name}")
            print(f"  Text: {script['text'][:60]}...")
            
            for param_name, params in PARAM_SETS.items():
                output_file = script_dir / f"{param_name}.wav"
                
                print(f"    {param_name}: exag={params['exaggeration']}, "
                      f"cfg={params['cfg_weight']}, temp={params['temperature']}")
                
                if dry_run:
                    print(f"      [DRY RUN] Would save to: {output_file}")
                else:
                    try:
                        wav = generate_audio(model, script["text"], voice_ref, params)
                        torchaudio.save(str(output_file), wav, model.sr)
                        print(f"      ✓ Saved: {output_file.name}")
                        
                        results["tests"].append({
                            "dj": dj,
                            "script": script_name,
                            "params": param_name,
                            "file": str(output_file),
                            "voice_ref": voice_ref,
                            "text_length": len(script["text"]),
                            "status": "success"
                        })
                    except Exception as e:
                        print(f"      ✗ Error: {e}")
                        results["tests"].append({
                            "dj": dj,
                            "script": script_name,
                            "params": param_name,
                            "error": str(e),
                            "status": "failed"
                        })
    
    # Save results manifest
    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*60}")
    print("A/B Test Complete!")
    print(f"{'='*60}")
    print(f"Output directory: {output_dir}")
    print(f"Manifest: {manifest_path}")
    print(f"\nTotal tests: {len(results['tests'])}")
    
    # Print listening guide
    print("\n" + "="*60)
    print("LISTENING GUIDE")
    print("="*60)
    print("""
For each script, compare the parameter sets:

1. BASELINE (exag=0.5, cfg=0.5, temp=0.8)
   - Chatterbox default exag/cfg with safe temperature
   - Higher CFG = more literal voice matching

2. WARM_NATURAL (exag=0.5, cfg=0.3, temp=0.8)
   - Lower CFG for more natural pacing
   - Good for conversational delivery

3. EXPRESSIVE_LOW_CFG (exag=0.6, cfg=0.3, temp=0.8)
   - More emotional peaks with natural pacing
   - Good for enthusiastic intros

4. SUBTLE_SMOOTH (exag=0.4, cfg=0.35, temp=0.7)
   - More controlled, less variability
   - Good for time/weather announcements

5. BALANCED (exag=0.5, cfg=0.35, temp=0.85)
   - Middle ground on all parameters
   - Good general-purpose setting

Listen for:
- Robotic/flat delivery (increase exaggeration)
- Rushing/unnatural pacing (lower CFG weight)
- Warbling/artifacts (lower exaggeration, lower temp)
- Gibberish/nonsense (temp was too high - now fixed at 0.8)
""")
    
    return output_dir


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="A/B test TTS parameters")
    parser.add_argument("--dj", choices=["julie", "mr_new_vegas", "both"], 
                        default="both", help="Which DJ to test")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be generated without running TTS")
    parser.add_argument("--fp16", action="store_true",
                        help="Use half precision (fp16) for faster but potentially lower quality")
    args = parser.parse_args()
    
    djs = ["julie", "mr_new_vegas"] if args.dj == "both" else [args.dj]
    run_ab_test(djs=djs, dry_run=args.dry_run, use_half=args.fp16)
