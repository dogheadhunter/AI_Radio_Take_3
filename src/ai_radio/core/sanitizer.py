"""Text sanitization and validation utilities for AI Radio scripts.

This module provides functions to clean and validate generated DJ scripts,
removing meta-commentary, fixing encoding issues, and validating content
appropriateness for different content types.
"""
import re
import logging

logger = logging.getLogger(__name__)


def sanitize_script(text: str, content_type: str = "intros") -> str:
    """Remove meta-commentary and sanitize TTS-breaking punctuation.
    
    Args:
        text: The script text to sanitize
        content_type: Type of content ('intros', 'outros', 'time', 'weather')
        
    Returns:
        Sanitized script text safe for TTS
    """
    # Strip leading/trailing quotes and whitespace
    text = text.strip().strip('"').strip("'").strip()
    
    # Time-specific sanitization
    if content_type == "time":
        # Remove timecode prefixes like "00:05" or "12:30" at start or end
        text = re.sub(r'^\d{1,2}:\d{2}\s+', '', text)
        text = re.sub(r'\s+\d{1,2}:\d{2}$', '', text)
        # Remove standalone timestamps anywhere
        text = re.sub(r'\b\d{1,2}:\d{2}(:\d{2})?\b', '', text)
        # Remove 24-hour format mentions
        text = re.sub(r'\b([01]?\d|2[0-3]):[0-5]\d\b', '', text)
    
    # Remove ALL parenthetical content (often meta-commentary)
    text = re.sub(r'\([^)]*\)', '', text)
    
    # Remove ALL bracketed content (stage directions, meta-text like [Music starts])
    text = re.sub(r'\[[^\]]*\]', '', text)
    
    # Remove dates/years
    text = re.sub(r'\b(19|20)\d{2}\b', '', text)  # Remove 4-digit years
    text = re.sub(r'\b\d{4}s\b', '', text)  # Remove decade references like "1940s"
    
    # Fix encoding issues (UTF-8 mojibake - when UTF-8 is read as Latin-1)
    mojibake_fixes = {
        'â€¦': '...',
        'â€™': "'",
        'â€˜': "'",
        'â€"': '-',
        'â€œ': '"',
        'â€': '"',
        '…': '...',
    }
    for bad, good in mojibake_fixes.items():
        text = text.replace(bad, good)
    
    # Fix TTS-breaking punctuation
    text = re.sub(r'([?!]),', r'\1', text)
    text = re.sub(r'\s*-\s*', ' ', text)
    
    # Clean up extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Fix ellipsis at sentence boundaries
    text = re.sub(r'\.{2,}', '.', text)
    
    # Fix double punctuation like "!." or "?." 
    text = re.sub(r'([!?])\.', r'\1', text)
    
    # Add missing spaces after punctuation
    text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)
    
    return text


def validate_time_announcement(text: str) -> tuple:
    """Rule-based validation for time announcements.
    
    Args:
        text: The time announcement script text
        
    Returns:
        Tuple of (passed: bool, reason: str)
    """
    if not text or not text.strip():
        return False, "Empty script"
    
    text = text.strip()
    word_count = len(text.split())
    
    # Length check: 1-2 sentences max (40 words is generous)
    if word_count > 40:
        return False, f"Too long ({word_count} words, max 40)"
    
    # Too short to be useful
    if word_count < 3:
        return False, f"Too short ({word_count} words)"
    
    # Check for specific artist/song patterns
    if re.search(r'\bby\s+[A-Z][a-z]+\s+[A-Z]', text):
        return False, "Contains likely artist reference"
    
    # Pattern: explicit labels
    if re.search(r'[Aa]rtist:|[Tt]itle:|[Ss]ong:', text):
        return False, "Contains explicit song/artist labels"
    
    # Check for timecode formats
    if re.search(r'\b\d{1,2}:\d{2}\b', text):
        return False, "Contains timecode format"
    
    # All checks passed
    return True, "OK"


def validate_weather_announcement(text: str) -> tuple:
    """Rule-based validation for weather announcements.
    
    Args:
        text: The weather announcement script text
        
    Returns:
        Tuple of (passed: bool, reason: str)
    """
    if not text or not text.strip():
        return False, "Empty script"
    
    text = text.strip()
    word_count = len(text.split())
    
    # Length check: 2-3 sentences (20-60 words)
    if word_count < 10:
        return False, f"Too short ({word_count} words, min 10)"
    
    if word_count > 80:
        return False, f"Too long ({word_count} words, max 80)"
    
    # Check for specific artist/song patterns (shouldn't be in weather)
    if re.search(r'\bby\s+[A-Z][a-z]+\s+[A-Z]', text):
        return False, "Contains likely artist reference"
    
    # Pattern: explicit labels
    if re.search(r'[Aa]rtist:|[Tt]itle:|[Ss]ong:', text):
        return False, "Contains explicit song/artist labels"
    
    # All checks passed
    return True, "OK"


def truncate_after_song_intro(text: str, artist: str, title: str) -> str:
    """Truncate any text that comes after the song introduction.
    
    This ensures intros stop after mentioning the artist and title,
    preventing rambling or additional commentary.
    
    Args:
        text: The full script text
        artist: Expected artist name
        title: Expected song title
        
    Returns:
        Truncated text ending at song introduction, or empty string if
        artist name appears truncated (potential LLM error)
    """
    # Validate artist name appears correctly (catch typos/truncations)
    # Returns empty string to signal invalid output that should be rejected
    artist_parts = artist.split()
    if len(artist_parts) > 1:
        for part in artist_parts:
            if len(part) > 3:
                pattern = re.escape(part[:4])
                if re.search(r'\b' + pattern + r'[a-z]{0,2}\b', text, re.IGNORECASE):
                    if part.lower() not in text.lower():
                        logger.warning(f"Detected truncated artist name in script: expected '{artist}'")
                        return ""  # Signal invalid output
    
    # Protect common abbreviations
    protected_text = text.replace('Mr.', 'Mr~').replace('Mrs.', 'Mrs~').replace('Ms.', 'Ms~').replace('Dr.', 'Dr~')
    
    # Split by punctuation but don't require space after (handles both "foo. bar" and "foo.bar")
    sentences = re.split(r'([.!?])\s*', protected_text)
    
    # Find the sentence containing the song intro (artist + title)
    intro_index = -1
    for i in range(0, len(sentences), 2):
        if i >= len(sentences):
            break
        sentence = sentences[i]
        has_artist = artist.lower() in sentence.lower()
        has_title = title.lower() in sentence.lower()
        
        if has_artist and has_title:
            intro_index = i
            break
    
    # If found, keep everything up to and including the intro sentence
    if intro_index >= 0:
        result = []
        for i in range(0, intro_index + 2, 2):  # +2 to include punctuation
            if i < len(sentences):
                result.append(sentences[i])
                if i + 1 < len(sentences):
                    result.append(sentences[i + 1])
                    # Add space after punctuation unless it's the last item
                    if i + 2 < intro_index + 2:
                        result.append(' ')
        
        final_text = ''.join(result).strip()
        # Restore protected abbreviations
        final_text = final_text.replace('Mr~', 'Mr.').replace('Mrs~', 'Mrs.').replace('Ms~', 'Ms.').replace('Dr~', 'Dr.')
        # Ensure spaces after punctuation (fix any remaining issues)
        final_text = re.sub(r'([.!?])([A-Z])', r'\1 \2', final_text)
        return final_text
    
    # No intro found - return original with spaces fixed
    text = text.replace('Mr~', 'Mr.').replace('Mrs~', 'Mrs.').replace('Ms~', 'Ms.').replace('Dr~', 'Dr.')
    text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)
    return text
