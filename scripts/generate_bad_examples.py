"""Generate intentionally bad scripts to test auditor failure detection.

These scripts violate key criteria to verify the auditor catches them.
"""
from pathlib import Path
import json
from datetime import datetime

# Bad script templates that should FAIL audit
BAD_TEMPLATES = [
    {
        "id": "bad_emoji",
        "dj": "julie",
        "content_type": "song_intro",
        "text": "Hey friends! 😀 This next track is totally awesome! 🎵 Here's All of Me by Billie Holiday. You're gonna love it! ❤️",
        "expected_issues": ["emojis", "modern slang (awesome)"]
    },
    {
        "id": "bad_modern_slang",
        "dj": "mr_new_vegas",
        "content_type": "song_intro",
        "text": "Yo, what's up New Vegas! This next track is lit, no cap. It's lowkey fire. Here's Blue Moon by Frank Sinatra - this song absolutely slaps!",
        "expected_issues": ["modern slang (yo, lit, no cap, lowkey, slaps)", "breaks character voice"]
    },
    {
        "id": "bad_character_break_julie",
        "dj": "julie",
        "content_type": "song_intro",
        "text": "Good evening, ladies and gentlemen of Appalachia. I present to you this exquisite vocal performance. Here is Billie Holiday with All of Me.",
        "expected_issues": ["wrong voice (too formal/polished for Julie)", "sounds like Mr. New Vegas"]
    },
    {
        "id": "bad_character_break_mr_nv",
        "dj": "mr_new_vegas",
        "content_type": "song_intro",
        "text": "Um, well, you know, I was just thinking, like, this next song is pretty good I guess? It's Blue Moon by Frank Sinatra. I don't know, what do you think?",
        "expected_issues": ["wrong voice (uncertain/questioning)", "sounds like Julie", "not confident/romantic"]
    },
    {
        "id": "bad_generic_radio",
        "dj": "julie",
        "content_type": "song_intro",
        "text": "Welcome back to the show! Hope you're having a great day. Don't forget to like and subscribe! Up next, it's Billie Holiday with All of Me. Stay tuned!",
        "expected_issues": ["modern radio clichés", "no character voice", "generic DJ speak"]
    },
]


def main():
    output_dir = Path("data/generated_bad")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for bad in BAD_TEMPLATES:
        filepath = output_dir / f"{bad['id']}_{timestamp}.json"
        
        data = {
            "script_id": bad["id"],
            "dj": bad["dj"],
            "content_type": bad["content_type"],
            "text": bad["text"],
            "expected_issues": bad["expected_issues"],
            "generated_at": timestamp,
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Generated {filepath.name}")
    
    print(f"\n✅ Created {len(BAD_TEMPLATES)} bad examples in {output_dir}")
    print(f"   Expected: All should FAIL audit with score < 6.0")


if __name__ == "__main__":
    main()
