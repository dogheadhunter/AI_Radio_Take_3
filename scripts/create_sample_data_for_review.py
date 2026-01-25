"""
Create sample generated content for testing the Review GUI.

This creates a minimal set of sample scripts and audio files
to demonstrate the Review GUI functionality.
"""
import json
from pathlib import Path
from datetime import datetime

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
GENERATED_DIR = DATA_DIR / "generated"

def create_sample_intro():
    """Create a sample intro."""
    folder = GENERATED_DIR / "intros" / "julie" / "Louis_Armstrong-A_Kiss_to_Build_a_Dream_On"
    folder.mkdir(parents=True, exist_ok=True)
    
    # Create sample script
    script = """Well hello there, friends! You're about to hear one of the most romantic tunes ever recorded - "A Kiss to Build a Dream On" by the legendary Louis Armstrong. His warm, gravelly voice makes this song feel like a warm hug from an old friend. Let's listen together!"""
    
    (folder / "julie_0.txt").write_text(script, encoding='utf-8')
    
    # Create dummy audio file (just a placeholder)
    (folder / "julie_0.wav").write_bytes(b"RIFF....WAVEfmt ")
    
    # Create review status
    review_status = {
        "status": "pending",
        "reviewed_at": None,
        "reviewer_notes": "",
        "script_issues": [],
        "audio_issues": []
    }
    (folder / "review_status.json").write_text(json.dumps(review_status, indent=2), encoding='utf-8')
    
    print(f"✓ Created sample intro: {folder.name}")


def create_sample_outro():
    """Create a sample outro."""
    folder = GENERATED_DIR / "outros" / "mr_new_vegas" / "Billie_Holiday-All_of_Me"
    folder.mkdir(parents=True, exist_ok=True)
    
    # Create sample script
    script = """That was Billie Holiday with "All of Me" - a true classic from the Mojave's favorite station. Stay tuned, more music coming your way."""
    
    (folder / "mr_new_vegas_outro.txt").write_text(script, encoding='utf-8')
    
    # Create dummy audio file
    (folder / "mr_new_vegas_outro.wav").write_bytes(b"RIFF....WAVEfmt ")
    
    # Create review status - this one is approved
    review_status = {
        "status": "approved",
        "reviewed_at": datetime.now().isoformat(),
        "reviewer_notes": "Perfect delivery and pacing",
        "script_issues": [],
        "audio_issues": []
    }
    (folder / "review_status.json").write_text(json.dumps(review_status, indent=2), encoding='utf-8')
    
    print(f"✓ Created sample outro: {folder.name}")


def create_sample_time():
    """Create a sample time announcement."""
    folder = GENERATED_DIR / "time" / "julie" / "12-00"
    folder.mkdir(parents=True, exist_ok=True)
    
    # Create sample script
    script = """It's high noon, friends! Time for lunch and some good music here on Appalachia Radio."""
    
    (folder / "julie_0.txt").write_text(script, encoding='utf-8')
    
    # Create dummy audio file
    (folder / "julie_0.wav").write_bytes(b"RIFF....WAVEfmt ")
    
    # Create review status - this one is rejected
    # Note: Use exact strings from SCRIPT_ISSUES["time"] in review_gui.py
    review_status = {
        "status": "rejected",
        "reviewed_at": datetime.now().isoformat(),
        "reviewer_notes": "Uses modern phrasing",
        "script_issues": ["Unnatural flow"],  # Changed to match exact option
        "audio_issues": []
    }
    (folder / "review_status.json").write_text(json.dumps(review_status, indent=2), encoding='utf-8')
    
    print(f"✓ Created sample time announcement: {folder.name}")


def create_sample_weather():
    """Create a sample weather announcement."""
    folder = GENERATED_DIR / "weather" / "mr_new_vegas" / "06-00"
    folder.mkdir(parents=True, exist_ok=True)
    
    # Create sample script - version 0
    script_v0 = """Good morning, wastelanders. It's 72 degrees out there, perfect weather for surviving another day in the Mojave."""
    
    (folder / "mr_new_vegas_0.txt").write_text(script_v0, encoding='utf-8')
    (folder / "mr_new_vegas_0.wav").write_bytes(b"RIFF....WAVEfmt ")
    
    # Create version 1 (regenerated)
    script_v1 = """Rise and shine, citizens of New Vegas. The temperature is a pleasant 72 degrees Fahrenheit with clear skies - another beautiful morning in the Mojave."""
    
    (folder / "mr_new_vegas_1.txt").write_text(script_v1, encoding='utf-8')
    (folder / "mr_new_vegas_1.wav").write_bytes(b"RIFF....WAVEfmt ")
    
    # Create review status
    review_status = {
        "status": "pending",
        "reviewed_at": None,
        "reviewer_notes": "Version 1 is much better",
        "script_issues": [],
        "audio_issues": []
    }
    (folder / "review_status.json").write_text(json.dumps(review_status, indent=2), encoding='utf-8')
    
    print(f"✓ Created sample weather announcement with 2 versions: {folder.name}")


def create_sample_audit_results():
    """Create sample audit results."""
    # Julie intro - passed
    audit_dir = DATA_DIR / "audit" / "julie" / "passed"
    audit_dir.mkdir(parents=True, exist_ok=True)
    
    audit_result = {
        "script_id": "Louis_Armstrong-A_Kiss_to_Build_a_Dream_On",
        "score": 8.5,
        "passed": True,
        "criteria_scores": {
            "character_voice": 9,
            "era_appropriateness": 8,
            "forbidden_elements": 10,
            "natural_flow": 8,
            "length": 8
        },
        "issues": [],
        "notes": "Good character voice, appropriate era references"
    }
    
    audit_file = audit_dir / "Louis_Armstrong-A_Kiss_to_Build_a_Dream_On_intro_audit.json"
    audit_file.write_text(json.dumps(audit_result, indent=2), encoding='utf-8')
    
    # Mr New Vegas outro - passed
    audit_dir = DATA_DIR / "audit" / "mr_new_vegas" / "passed"
    audit_dir.mkdir(parents=True, exist_ok=True)
    
    audit_result = {
        "script_id": "Billie_Holiday-All_of_Me",
        "score": 9.0,
        "passed": True,
        "criteria_scores": {
            "character_voice": 9,
            "era_appropriateness": 9,
            "forbidden_elements": 10,
            "natural_flow": 9,
            "length": 8
        },
        "issues": [],
        "notes": "Excellent outro, matches character perfectly"
    }
    
    audit_file = audit_dir / "Billie_Holiday-All_of_Me_outro_audit.json"
    audit_file.write_text(json.dumps(audit_result, indent=2), encoding='utf-8')
    
    # Julie time - failed
    audit_dir = DATA_DIR / "audit" / "julie" / "failed"
    audit_dir.mkdir(parents=True, exist_ok=True)
    
    audit_result = {
        "script_id": "12-00",
        "score": 5.5,
        "passed": False,
        "criteria_scores": {
            "character_voice": 7,
            "natural_flow": 6,
            "brevity": 4
        },
        "issues": ["Uses modern phrasing 'high noon'"],
        "notes": "Too modern for the era"
    }
    
    audit_file = audit_dir / "12-00_time_audit.json"
    audit_file.write_text(json.dumps(audit_result, indent=2), encoding='utf-8')
    
    print("✓ Created sample audit results")


def create_empty_regen_queue():
    """Create an empty regeneration queue file."""
    queue_file = DATA_DIR / "regeneration_queue.json"
    queue_file.write_text("[]", encoding='utf-8')
    print("✓ Created empty regeneration queue")


def main():
    """Create all sample data."""
    print("Creating sample data for Review GUI testing...")
    print()
    
    # Create sample content
    create_sample_intro()
    create_sample_outro()
    create_sample_time()
    create_sample_weather()
    
    print()
    
    # Create audit results
    create_sample_audit_results()
    
    print()
    
    # Create empty queue
    create_empty_regen_queue()
    
    print()
    print("✅ Sample data created successfully!")
    print()
    print("You can now run the Review GUI:")
    print("  python run_review_gui.py")
    print()
    print("Sample content created:")
    print("  - 1 intro (Julie, pending review)")
    print("  - 1 outro (Mr. New Vegas, approved)")
    print("  - 1 time announcement (Julie, rejected)")
    print("  - 1 weather announcement (Mr. New Vegas, 2 versions)")


if __name__ == "__main__":
    main()
