#!/usr/bin/env python
"""Demo script showing cherry picker usage.

This demonstrates how to use the cherry picker module to select
the best script from multiple versions.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ai_radio.cherry_picker import CherryPicker, SelectionGuidelines

# Example: Three versions of a Julie intro script
def demo_basic_selection():
    """Demonstrate basic script selection."""
    print("=" * 60)
    print("CHERRY PICKER DEMO: Basic Selection")
    print("=" * 60)
    
    # Create temporary scripts for demo
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        
        # Version 0: Original (fails audit)
        v0 = tmp / "julie_0.txt"
        v0.write_text("This song is awesome! It's so cool and modern.")
        
        # Version 1: First regeneration (passes but not great)
        v1 = tmp / "julie_1.txt"
        v1.write_text("Here's a song for you, friends.")
        
        # Version 2: Second regeneration (best - warm, era-appropriate)
        v2 = tmp / "julie_2.txt"
        v2.write_text("Welcome home, neighbors. Let's gather 'round for this beautiful tune from the hills.")
        
        # Mock audit results
        audit_results = {
            v0: {
                "passed": False,
                "score": 3.5,
                "criteria_scores": {
                    "character_voice": 4.0,
                    "era_appropriateness": 3.0,
                    "natural_flow": 4.0
                },
                "issues": ["Modern slang: awesome, cool"]
            },
            v1: {
                "passed": True,
                "score": 7.0,
                "criteria_scores": {
                    "character_voice": 7.0,
                    "era_appropriateness": 7.0,
                    "natural_flow": 7.0
                },
                "issues": []
            },
            v2: {
                "passed": True,
                "score": 9.0,
                "criteria_scores": {
                    "character_voice": 9.0,
                    "era_appropriateness": 9.0,
                    "natural_flow": 9.0
                },
                "issues": []
            }
        }
        
        # Run cherry picker
        picker = CherryPicker()
        guidelines = SelectionGuidelines(
            require_audit_pass=True,
            style_weight=2.0,  # Emphasize Julie's personality
        )
        
        result = picker.pick_best(
            script_paths=[v0, v1, v2],
            audit_results=audit_results,
            guidelines=guidelines,
            dj="julie"
        )
        
        # Display results
        print(f"\n🏆 WINNER: {result.winner_path.name}")
        print(f"Content: {result.winner_content}")
        print(f"\nRationale: {result.selection_rationale}")
        
        print("\n📊 FULL RANKINGS:")
        for ranking in result.rankings:
            print(f"\n  Rank #{ranking.rank}: {ranking.path.name}")
            print(f"    Overall Score: {ranking.overall_score:.2f}")
            print(f"    {ranking.rationale}")
            print(f"    Scores: {ranking.guideline_scores}")


def demo_custom_weights():
    """Demonstrate custom weight configuration."""
    print("\n\n" + "=" * 60)
    print("CHERRY PICKER DEMO: Custom Weights")
    print("=" * 60)
    
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        
        # Script 1: Very concise but lacks personality
        s1 = tmp / "concise.txt"
        s1.write_text("Here's a song.")
        
        # Script 2: Verbose but full of Julie's warmth
        s2 = tmp / "warm.txt"
        s2.write_text(
            "Well now, friends and neighbors, gather 'round! "
            "I've got a wonderful tune here that reminds me of home, "
            "of the hills of Appalachia, and all the good folks there."
        )
        
        audit_results = {
            s1: {
                "passed": True,
                "score": 7.0,
                "criteria_scores": {
                    "character_voice": 6.0,
                    "era_appropriateness": 7.0,
                    "natural_flow": 7.0,
                    "length": 10.0  # Very concise
                }
            },
            s2: {
                "passed": True,
                "score": 8.5,
                "criteria_scores": {
                    "character_voice": 9.5,
                    "era_appropriateness": 9.0,
                    "natural_flow": 8.0,
                    "length": 6.0  # A bit long
                }
            }
        }
        
        picker = CherryPicker()
        
        # Scenario A: Emphasize conciseness
        print("\n📏 SCENARIO A: Emphasize Conciseness")
        guidelines_a = SelectionGuidelines(
            conciseness_weight=5.0,
            style_weight=1.0
        )
        result_a = picker.pick_best([s1, s2], audit_results, guidelines_a, dj="julie")
        print(f"  Winner: {result_a.winner_path.name}")
        print(f"  Rationale: {result_a.selection_rationale}")
        
        # Scenario B: Emphasize personality/style
        print("\n🎭 SCENARIO B: Emphasize Personality/Style")
        guidelines_b = SelectionGuidelines(
            conciseness_weight=0.5,
            style_weight=3.0,
            creativity_weight=2.0
        )
        result_b = picker.pick_best([s1, s2], audit_results, guidelines_b, dj="julie")
        print(f"  Winner: {result_b.winner_path.name}")
        print(f"  Rationale: {result_b.selection_rationale}")


def demo_forced_pick():
    """Demonstrate forced pick (user override)."""
    print("\n\n" + "=" * 60)
    print("CHERRY PICKER DEMO: Forced Pick Override")
    print("=" * 60)
    
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        
        s1 = tmp / "best.txt"
        s1.write_text("This is objectively the best script.")
        
        s2 = tmp / "user_choice.txt"
        s2.write_text("But the user wants this one.")
        
        audit_results = {
            s1: {"passed": True, "score": 9.5, "criteria_scores": {"character_voice": 9.5}},
            s2: {"passed": True, "score": 7.0, "criteria_scores": {"character_voice": 7.0}},
        }
        
        picker = CherryPicker()
        
        # Without forced pick
        print("\n🤖 WITHOUT FORCED PICK:")
        result_auto = picker.pick_best([s1, s2], audit_results)
        print(f"  Automatic selection: {result_auto.winner_path.name}")
        
        # With forced pick
        print("\n👤 WITH FORCED PICK:")
        guidelines = SelectionGuidelines(forced_pick=s2)
        result_forced = picker.pick_best([s1, s2], audit_results, guidelines)
        print(f"  User override: {result_forced.winner_path.name}")
        print(f"  Rationale: {result_forced.selection_rationale}")


if __name__ == "__main__":
    print("\n🍒 CHERRY PICKER MODULE DEMO\n")
    
    try:
        demo_basic_selection()
        demo_custom_weights()
        demo_forced_pick()
        
        print("\n\n" + "=" * 60)
        print("✅ Demo complete!")
        print("=" * 60)
        print("\nFor integration into pipeline, see:")
        print("  docs/CHERRY_PICKER_INTEGRATION.md")
        print("\nFor API documentation, see:")
        print("  src/ai_radio/cherry_picker.py docstrings")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
