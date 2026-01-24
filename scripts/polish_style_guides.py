"""
Polish style guides to achieve solid pass quality.

Fixes:
1. Replace {c} placeholders with actual counts
2. Add example usage to vocabulary tables
3. Enhance intro/outro patterns with better examples
4. Clean sentence starters artifacts
5. Expand Mr. New Vegas romantic phrasing to 20+ examples
6. Reorganize sections for consistency
"""

import json
import re
from collections import Counter
from pathlib import Path

# Load categorized data
with open("data/style_analysis/julie_categorized.json") as f:
    julie_data = json.load(f)

with open("data/style_analysis/mr_new_vegas_categorized.json") as f:
    mr_nv_data = json.load(f)

def get_word_counts(segments, words):
    """Count occurrences of specific words across all segments."""
    all_text = " ".join(segments).lower()
    counts = {}
    for word in words:
        pattern = r'\b' + re.escape(word.lower()) + r'\b'
        counts[word] = len(re.findall(pattern, all_text))
    return counts

def find_usage_examples(segments, word, max_examples=2):
    """Find example sentences containing the word."""
    examples = []
    word_pattern = r'\b' + re.escape(word.lower()) + r'\b'
    
    for seg in segments:
        if re.search(word_pattern, seg.lower()) and len(examples) < max_examples:
            # Get a short excerpt
            sentences = seg.split('.')
            for sent in sentences:
                if re.search(word_pattern, sent.lower()):
                    clean = sent.strip()
                    if clean and len(clean) < 120:
                        examples.append(clean)
                        break
    
    return examples[:max_examples]

# Julie vocabulary with counts and examples
julie_all_segments = []
for category in julie_data.values():
    julie_all_segments.extend(category)

julie_vocab_words = ["it's", "song", "here", "one", "about", "just", "next", 
                     "like", "there", "can", "here's", "out", "friends", 
                     "get", "know", "don't", "time", "radio", "i'm"]

julie_vocab_counts = get_word_counts(julie_all_segments, julie_vocab_words)

# Mr. New Vegas vocabulary
mr_nv_all_segments = []
for category in mr_nv_data.values():
    mr_nv_all_segments.extend(category)

mr_nv_vocab_words = ["new", "ncr", "vegas", "been", "news", "one", 
                     "camp", "now", "legion", "right", "report", "dam",
                     "coming", "love", "got", "some", "about"]

mr_nv_vocab_counts = get_word_counts(mr_nv_all_segments, mr_nv_vocab_words)

# Find better intro/outro examples for Julie
julie_song_intros = julie_data["song_intro"]
julie_song_outros = julie_data["song_outro"]

# Filter out generic/weak examples
strong_julie_intros = [
    intro for intro in julie_song_intros 
    if len(intro) > 20 and not intro.startswith("Untitled")
][:10]

strong_julie_outros = [
    outro for outro in julie_song_outros
    if len(outro) > 15
][:6]

# Mr. New Vegas intros/outros
mr_nv_intros = mr_nv_data["song_intro"]
mr_nv_outros = mr_nv_data["song_outro"]

strong_mr_nv_intros = [
    intro for intro in mr_nv_intros
    if len(intro) > 20
][:10]

strong_mr_nv_outros = [
    outro for outro in mr_nv_outros
    if len(outro) > 10
][:6]

# Find additional romantic phrasing for Mr. New Vegas
romantic_keywords = ["love", "special", "beautiful", "feeling", "heart", "romance",
                     "dear", "darling", "kiss", "embrace", "wonderful"]

mr_nv_romantic = []
for seg in mr_nv_all_segments:
    seg_lower = seg.lower()
    if any(kw in seg_lower for kw in romantic_keywords) and len(seg) > 30:
        if seg not in mr_nv_romantic:
            mr_nv_romantic.append(seg)
            if len(mr_nv_romantic) >= 25:
                break

# Clean sentence starters (remove artifacts)
def clean_starter(starter):
    """Remove timestamp and file artifacts."""
    # Remove "Untitled - January 23, 2026 Now" pattern
    cleaned = re.sub(r'^Untitled - \w+ \d+, \d+ Now\s*', '', starter)
    # Remove just "Untitled"
    cleaned = re.sub(r'^Untitled\s*-?\s*', '', cleaned)
    return cleaned.strip()

print("=" * 60)
print("JULIE ENHANCEMENTS")
print("=" * 60)

print("\n📊 Vocabulary Counts:")
for word in sorted(julie_vocab_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {word[0]}: {word[1]}")

print(f"\n🎵 Strong Intros: {len(strong_julie_intros)}")
for i, intro in enumerate(strong_julie_intros[:3], 1):
    print(f"  {i}. {intro[:80]}...")

print(f"\n🎤 Strong Outros: {len(strong_julie_outros)}")
for i, outro in enumerate(strong_julie_outros[:3], 1):
    print(f"  {i}. {outro[:60]}...")

print("\n" + "=" * 60)
print("MR. NEW VEGAS ENHANCEMENTS")
print("=" * 60)

print("\n📊 Vocabulary Counts:")
for word in sorted(mr_nv_vocab_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {word[0]}: {word[1]}")

print(f"\n🎵 Strong Intros: {len(strong_mr_nv_intros)}")
for i, intro in enumerate(strong_mr_nv_intros[:3], 1):
    print(f"  {i}. {intro[:80]}...")

print(f"\n💕 Romantic Phrases Found: {len(mr_nv_romantic)}")
for i, phrase in enumerate(mr_nv_romantic[:5], 1):
    print(f"  {i}. {phrase[:60]}...")

print("\n" + "=" * 60)
print("✅ Analysis complete! Ready to update style guides.")
print("=" * 60)
