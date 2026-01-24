"""
Rule-based validator for script quality.

Fast, deterministic checks that must pass before LLM evaluation.
These catch objective issues that an LLM might miss.
"""
import re
from dataclasses import dataclass, field
from typing import List, Tuple, Optional


@dataclass
class RuleValidationResult:
    """Result of rule-based validation."""
    passed: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class RuleBasedValidator:
    """
    Validates scripts using deterministic rules.
    
    Catches:
    - Encoding issues (malformed UTF-8)
    - Punctuation errors (double periods, unbalanced quotes)
    - Grammar basics (incomplete sentences)
    - Structure requirements (must end with song intro)
    - Forbidden content (emojis, meta-commentary)
    """
    
    # Common malformed character sequences (UTF-8 encoding errors)
    # These appear when UTF-8 is double-encoded or misinterpreted as Windows-1252
    MALFORMED_PATTERNS = [
        r'â€¦',  # Ellipsis encoded wrong
        r'â€™',  # Apostrophe encoded wrong
        r'â€˜',  # Left single quote
        r'â€œ',  # Opening quote encoded wrong
        r'â€',   # Generic encoding issue (partial)
        r'Ã©',   # Accented e encoded wrong
        r'Ã¨',   # Another accent issue
        r'Ã ',   # Accented a
        r'â€"',  # Em-dash encoded wrong
        r'â€"',  # En-dash
        # Raw Unicode sequences that indicate encoding issues
        r'\u00e2\u20ac',  # Common UTF-8 misread prefix
    ]
    
    # Pattern to catch any remaining â followed by special characters
    ENCODING_ISSUE_PATTERN = re.compile(r'â[€™˜œ""\u20ac\u2122\u0153\u00a6]+', re.UNICODE)
    
    # Forbidden patterns
    EMOJI_PATTERN = re.compile(
        r'[\U0001F600-\U0001F64F'  # Emoticons
        r'\U0001F300-\U0001F5FF'   # Symbols & pictographs
        r'\U0001F680-\U0001F6FF'   # Transport & map
        r'\U0001F700-\U0001F77F'   # Alchemical
        r'\U0001F780-\U0001F7FF'   # Geometric shapes extended
        r'\U0001F800-\U0001F8FF'   # Supplemental arrows
        r'\U0001F900-\U0001F9FF'   # Supplemental symbols
        r'\U0001FA00-\U0001FA6F'   # Chess symbols
        r'\U0001FA70-\U0001FAFF'   # Symbols and pictographs extended
        r'\U00002702-\U000027B0'   # Dingbats
        r'\U0001F1E0-\U0001F1FF'   # Flags
        r']'
    )
    
    # Generic clichés that should be avoided
    GENERIC_CLICHES = [
        r'\byour local radio station\b',
        r'\bwelcome back\b',
        r'\bstay tuned\b',
        r'\blike and subscribe\b',
        r'\btimeless classic\b',
        r'\btrip down memory lane\b',
        r'\bgolden oldies\b',
    ]
    
    # Metadata patterns that shouldn't appear in scripts
    METADATA_PATTERNS = [
        r'\(take\)',
        r'\(version\)',
        r'\(demo\)',
        r'\(live\)',
        r'\(remaster\)',
    ]
    
    # Meta-commentary patterns
    META_PATTERNS = [
        r'\([^)]*(?:intro|outro|sentence|word|script|example)[^)]*\)',  # (1 sentence intro...)
        r'\[.*?\]',  # [notes in brackets]
        r'<.*?>',    # <tags>
    ]
    
    def __init__(self, content_type: str = "song_intro"):
        self.content_type = content_type
    
    def validate(
        self, 
        text: str, 
        artist: Optional[str] = None, 
        title: Optional[str] = None
    ) -> RuleValidationResult:
        """
        Run all validation rules on the script.
        
        Returns RuleValidationResult with passed=False if any critical rule fails.
        """
        errors = []
        warnings = []
        
        # Check encoding
        enc_errors = self._check_encoding(text)
        errors.extend(enc_errors)
        
        # Check punctuation
        punct_errors, punct_warnings = self._check_punctuation(text)
        errors.extend(punct_errors)
        warnings.extend(punct_warnings)
        
        # Check forbidden content
        forbidden_errors = self._check_forbidden(text)
        errors.extend(forbidden_errors)
        
        # Check structure (for song intros/outros)
        if self.content_type in ("song_intro", "song_outro") and artist and title:
            struct_errors, struct_warnings = self._check_structure(text, artist, title)
            errors.extend(struct_errors)
            warnings.extend(struct_warnings)
        
        # Check grammar basics
        grammar_warnings = self._check_grammar(text)
        warnings.extend(grammar_warnings)
        
        passed = len(errors) == 0
        return RuleValidationResult(passed=passed, errors=errors, warnings=warnings)
    
    def _check_encoding(self, text: str) -> List[str]:
        """Check for malformed character sequences."""
        errors = []
        for pattern in self.MALFORMED_PATTERNS:
            if pattern in text:
                errors.append(f"Malformed encoding: '{pattern}' found in text")
        
        # Also check the broader pattern for â + special chars
        match = self.ENCODING_ISSUE_PATTERN.search(text)
        if match:
            errors.append(f"Encoding issue detected: '{match.group()}' found in text")
        
        return errors
    
    def _check_punctuation(self, text: str) -> Tuple[List[str], List[str]]:
        """Check for punctuation errors."""
        errors = []
        warnings = []
        
        # Double periods
        if '..' in text and '...' not in text:
            errors.append("Double period '..' found - should be single '.'")
        
        # Triple+ periods not converted to ellipsis
        if '....' in text:
            errors.append("Four+ periods found - fix ellipsis handling")
        
        # Unbalanced quotes
        single_quotes = text.count("'") - text.count("n't") - text.count("'s") - text.count("'re") - text.count("'m") - text.count("'ll") - text.count("'ve") - text.count("'d")
        double_quotes = text.count('"')
        if double_quotes % 2 != 0:
            warnings.append("Unbalanced double quotes")
        
        # Missing period at end (unless ends with ! or ?)
        stripped = text.strip()
        if stripped and stripped[-1] not in '.!?':
            errors.append("Script does not end with proper punctuation (. ! ?)")
        
        # Question mark comma issue (,?)
        if ',?' in text or '?,' in text:
            errors.append("Invalid punctuation combination ',?' or '?,'")
        
        # Period after punctuation (.! or .?)
        if '.!' in text or '.?' in text:
            warnings.append("Unusual punctuation: period before ! or ?")
        
        return errors, warnings
    
    def _check_forbidden(self, text: str) -> List[str]:
        """Check for forbidden content."""
        errors = []
        
        # Emojis
        if self.EMOJI_PATTERN.search(text):
            errors.append("Script contains emoji - forbidden")
        
        # Meta-commentary
        for pattern in self.META_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                match = re.search(pattern, text, re.IGNORECASE)
                errors.append(f"Meta-commentary found: '{match.group()}'")
                break
        
        # Placeholder text
        placeholder_patterns = [
            r'\bArtist\s+\d+\b',
            r'\bTest\s+(?:Song|Artist)\b',
            r'\b(?:PLACEHOLDER|TODO|FIXME)\b',
        ]
        for pattern in placeholder_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                errors.append(f"Placeholder text found matching: {pattern}")
        
        # Dates/years (unless in song title context)
        year_pattern = r'\b(19|20)\d{2}\b'
        if re.search(year_pattern, text):
            errors.append("Year/date mentioned - should be removed")
        
        # Generic clichés
        for pattern in self.GENERIC_CLICHES:
            if re.search(pattern, text, re.IGNORECASE):
                match = re.search(pattern, text, re.IGNORECASE)
                errors.append(f"Generic cliché found: '{match.group()}'")
        
        # Metadata patterns
        for pattern in self.METADATA_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                match = re.search(pattern, text, re.IGNORECASE)
                errors.append(f"Metadata leak found: '{match.group()}'")
        
        return errors
    
    def _check_structure(
        self, 
        text: str, 
        artist: str, 
        title: str
    ) -> Tuple[List[str], List[str]]:
        """Check script structure for song intros."""
        errors = []
        warnings = []
        
        # For song intros, should mention artist OR title somewhere
        has_artist = artist.lower() in text.lower()
        has_title = title.lower() in text.lower()
        
        if not has_artist and not has_title:
            errors.append(f"Script doesn't mention artist '{artist}' or title '{title}'")
        elif not has_artist:
            warnings.append(f"Script doesn't mention artist '{artist}'")
        elif not has_title:
            warnings.append(f"Script doesn't mention title '{title}'")
        
        # Check that song mention is near the end (last 30% of text)
        text_lower = text.lower()
        artist_pos = text_lower.rfind(artist.lower()) if has_artist else -1
        title_pos = text_lower.rfind(title.lower()) if has_title else -1
        
        last_mention = max(artist_pos, title_pos)
        if last_mention > 0:
            # Check if there's significant text after the last mention
            text_after = text[last_mention:].lower()
            # Find where the artist/title mention ends
            mention_end = len(artist) if artist_pos >= title_pos else len(title)
            remaining = text[last_mention + mention_end:].strip()
            # Allow some closing (period, exclamation) but not new sentences
            if len(remaining) > 30:  # More than a closing phrase
                warnings.append("Significant text after song introduction")
        
        return errors, warnings
    
    def _check_grammar(self, text: str) -> List[str]:
        """Basic grammar checks - returns warnings only."""
        warnings = []
        
        # Sentence without verb (very basic check)
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 5 and len(sentence.split()) < 2:
                warnings.append(f"Possible incomplete sentence: '{sentence[:30]}...'")
        
        # Run-on sentences (very long without punctuation)
        words = text.split()
        word_count = len(words)
        if word_count > 100:
            warnings.append(f"Script may be too long: {word_count} words (max recommended: 80)")
        elif word_count > 80:
            warnings.append(f"Script is lengthy: {word_count} words")
        
        return warnings


def validate_script(
    text: str,
    content_type: str = "song_intro",
    artist: Optional[str] = None,
    title: Optional[str] = None,
) -> RuleValidationResult:
    """
    Convenience function to validate a script.
    
    Args:
        text: The script content to validate
        content_type: Type of content (song_intro, song_outro, weather, time)
        artist: Artist name (for song intros/outros)
        title: Song title (for song intros/outros)
    
    Returns:
        RuleValidationResult with passed status and any errors/warnings
    """
    validator = RuleBasedValidator(content_type=content_type)
    return validator.validate(text, artist=artist, title=title)
