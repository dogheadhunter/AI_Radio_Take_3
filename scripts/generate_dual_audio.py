#!/usr/bin/env python3
"""
Generate dual audio versions for all scripts using two voice references.

Generates TTS audio for all scripts using Turbo model with:
- 30 second voice clip
- Full voice clip

This provides two options per script for selection or regeneration.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
import torchaudio
from tqdm import tqdm

# Baseline parameters
PARAMS = {
    "exaggeration": 0.5,
    "cfg_weight": 0.5,
    "temperature": 0.8,
}


def load_chatterbox_turbo():
    """Load Chatterbox Turbo model."""
    chatterbox_path = Path(__file__).parent.parent / "chatterbox" / "src"
    if str(chatterbox_path) not in sys.path:
        sys.path.insert(0, str(chatterbox_path))
    
    from chatterbox.tts_turbo import ChatterboxTurboTTS
    
    print("Loading Chatterbox Turbo on cuda...")
    
    # Enable CUDA optimizations
    torch.backends.cudnn.benchmark = True
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    
    model = ChatterboxTurboTTS.from_pretrained(device="cuda")
    return model


def get_all_scripts(dj: str, script_types: list = None):
    """Get all scripts for specified types."""
    if script_types is None:
        script_types = ["intros", "outros", "time", "weather"]
    
    base_path = Path("data/generated")
    scripts = []
    
    for script_type in script_types:
        type_path = base_path / script_type / dj
        if not type_path.exists():
            continue
            
        for script_dir in type_path.iterdir():
            if not script_dir.is_dir():
                continue
                
            txt_files = list(script_dir.glob("*.txt"))
            if txt_files:
                text = txt_files[0].read_text(encoding="utf-8")
                scripts.append({
                    "type": script_type,
                    "name": script_dir.name,
                    "dir": script_dir,
                    "text": text,
                })
    
    return scripts


def generate_dual_audio(dj: str = "mr_new_vegas", dry_run: bool = False):
    """Generate audio with two voice references for all scripts."""
    
    # Voice references - generate both versions
    voice_refs = {
        "30sec": f"assets/voice_references/Mister_New_Vegas/mr_new_vegas_30sec.wav",
        "full": f"assets/voice_references/Mister_New_Vegas/mr_new_vegas.wav",
    }
    
    # Verify voice refs exist
    for name, path in voice_refs.items():
        if not Path(path).exists():
            print(f"ERROR: Voice reference not found: {path}")
            return
    
    # Get all scripts
    scripts = get_all_scripts(dj)
    print(f"Found {len(scripts)} scripts:")
    
    # Count by type
    type_counts = {}
    for s in scripts:
        type_counts[s['type']] = type_counts.get(s['type'], 0) + 1
    for t, c in type_counts.items():
        print(f"  {t}: {c}")
    
    total_generations = len(scripts) * len(voice_refs)
    print(f"\nWill generate {total_generations} audio files ({len(scripts)} scripts × {len(voice_refs)} voice refs)")
    
    if dry_run:
        print("\n[DRY RUN] - Not generating audio")
        return
    
    # Load model
    print()
    model = load_chatterbox_turbo()
    print()
    
    # Generate audio
    success_count = 0
    error_count = 0
    skipped_count = 0
    
    for script in tqdm(scripts, desc="Generating audio"):
        script_dir = script["dir"]
        
        # Generate both versions
        for ref_name, ref_path in voice_refs.items():
            # Name files by voice reference type: mr_new_vegas_0_30sec.wav, mr_new_vegas_0_full.wav
            output_file = script_dir / f"{dj}_0_{ref_name}.wav"
            
            # Skip if already exists
            if output_file.exists():
                tqdm.write(f"  ⊙ Skipping {script['type']}/{script['name']} ({ref_name}) - already exists")
                skipped_count += 1
                continue
            
            try:
                wav = model.generate(
                    text=script["text"],
                    audio_prompt_path=ref_path,
                    **PARAMS
                )
                torchaudio.save(str(output_file), wav, model.sr)
                tqdm.write(f"  ✓ Generated {script['type']}/{script['name']} ({ref_name})")
                success_count += 1
            except Exception as e:
                tqdm.write(f"  ✗ Error {script['type']}/{script['name']} ({ref_name}): {e}")
                error_count += 1
    
    print(f"\n{'='*60}")
    print(f"Generation complete!")
    print(f"  Generated: {success_count}")
    print(f"  Skipped (existing): {skipped_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total expected: {total_generations}")
    print(f"{'='*60}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate dual audio versions")
    parser.add_argument("--dj", default="mr_new_vegas", help="Which DJ to generate for")
    parser.add_argument("--dry-run", action="store_true", help="Show plan without generating")
    args = parser.parse_args()
    
    generate_dual_audio(dj=args.dj, dry_run=args.dry_run)
