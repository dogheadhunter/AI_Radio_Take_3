"""Cherry Picker: Script batch selection module.

This module evaluates multiple script versions (e.g., from regeneration cycles)
and selects the best candidate based on configurable guidelines.

Architecture:
- Standalone module, not yet integrated into pipeline stages
- Designed for eventual integration as an alternative to "last-pass-wins" logic
- Extensible guideline system for continuous refinement

Usage:
    from src.ai_radio.cherry_picker import CherryPicker, SelectionGuidelines
    
    picker = CherryPicker()
    guidelines = SelectionGuidelines(
        require_audit_pass=True,
        clarity_weight=1.5,
        style_weight=2.0
    )
    
    result = picker.pick_best(
        script_paths=["intro_v0.txt", "intro_v1.txt", "intro_v2.txt"],
        audit_results={"intro_v0.txt": {...}, ...},
        guidelines=guidelines
    )
    
    print(f"Winner: {result.winner_path}")
    for ranking in result.rankings:
        print(f"  {ranking.path}: {ranking.score} - {ranking.rationale}")

Extension Points:
- Add new guideline criteria by extending `_score_*` methods
- Customize weights in SelectionGuidelines
- Override `_rank_scripts()` for different selection algorithms
- Add external feedback integration (user reviews, TTS quality metrics)
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Any
import re
import json
import logging

logger = logging.getLogger(__name__)


# DJ-specific style markers (for bonus scoring)
DJ_STYLE_MARKERS = {
    "julie": ["friend", "neighbor", "folks", "home", "appalachia"],
    "mr.newvegas": ["lovely", "wonderful", "beautiful", "enchanting", "desert"],  # "mr. new vegas" normalized
    "mrnewvegas": ["lovely", "wonderful", "beautiful", "enchanting", "desert"],
}

# Common filler words to penalize (reduce conciseness)
FILLER_WORDS = ["actually", "basically", "literally", "um", "uh", "like", "you know"]


@dataclass
class ScriptCandidate:
    """Represents a script candidate for evaluation."""
    path: Path
    content: str
    audit_result: Optional[Dict[str, Any]] = None
    version: int = 0  # 0 = original, 1+ = regenerated
    
    @property
    def passed_audit(self) -> bool:
        """Check if script passed automated audit."""
        if not self.audit_result:
            return False
        return self.audit_result.get("passed", False)
    
    @property
    def audit_score(self) -> float:
        """Get audit score (0-10)."""
        if not self.audit_result:
            return 0.0
        return float(self.audit_result.get("score", 0.0))
    
    @property
    def audit_issues(self) -> List[str]:
        """Get list of audit issues."""
        if not self.audit_result:
            return []
        return self.audit_result.get("issues", [])


@dataclass
class SelectionGuidelines:
    """Configurable guidelines for script selection.
    
    All weights are multiplicative factors applied to individual criterion scores.
    Higher weights = more important criterion.
    """
    # Core requirement
    require_audit_pass: bool = True
    
    # Guideline weights (multiplicative, default 1.0)
    clarity_weight: float = 1.0          # Grammar, readability
    style_weight: float = 1.5            # Era/DJ personality compliance
    creativity_weight: float = 1.2       # Personality, distinct voice
    conciseness_weight: float = 1.0      # Brevity, no filler
    tts_safety_weight: float = 1.3       # TTS-friendly phrasing
    novelty_weight: float = 0.8          # Penalize near-duplicates
    
    # Thresholds
    min_clarity_score: float = 6.0       # Minimum acceptable clarity (0-10)
    min_style_score: float = 6.0         # Minimum acceptable style (0-10)
    max_length_chars: int = 500          # Maximum script length
    
    # Forbidden patterns (case-insensitive)
    # Note: Radio content is set in 2077 (Fallout universe), so modern years are anachronistic
    forbidden_patterns: List[str] = field(default_factory=lambda: [
        r'\b(awesome|cool|okay|ok)\b',      # Modern slang
        r'\b(lol|omg|btw)\b',               # Internet slang
        r'\b(19\d{2}|20\d{2}|21\d{2})\b',  # Years 1900-2199 (anachronistic)
    ])
    
    # User override (if provided, this script wins regardless)
    forced_pick: Optional[Path] = None


@dataclass
class ScriptRanking:
    """Ranking information for a single script."""
    path: Path
    overall_score: float
    guideline_scores: Dict[str, float]  # Individual criterion scores
    rationale: str                      # Human-readable explanation
    rank: int                           # 1 = best, 2 = second best, etc.


@dataclass
class SelectionResult:
    """Result of cherry picking operation."""
    winner_path: Path
    winner_content: str
    rankings: List[ScriptRanking]       # All candidates ranked
    selection_rationale: str            # Why winner was chosen


class CherryPicker:
    """Evaluates and selects the best script from a batch of candidates.
    
    Uses configurable guidelines to rank scripts and select the winner.
    """
    
    def __init__(self):
        """Initialize cherry picker."""
        pass
    
    def pick_best(
        self,
        script_paths: List[Path],
        audit_results: Dict[Path, Dict[str, Any]],
        guidelines: Optional[SelectionGuidelines] = None,
        dj: Optional[str] = None
    ) -> SelectionResult:
        """Select the best script from a batch of candidates.
        
        Args:
            script_paths: List of paths to script files
            audit_results: Dictionary mapping paths to audit result dicts
            guidelines: Selection guidelines (uses defaults if None)
            dj: DJ name for context (optional, used for style checking)
        
        Returns:
            SelectionResult with winner and rankings
        
        Raises:
            ValueError: If no valid candidates or no scripts pass requirements
        """
        if not script_paths:
            raise ValueError("No script paths provided")
        
        guidelines = guidelines or SelectionGuidelines()
        
        # Handle forced pick
        if guidelines.forced_pick:
            if guidelines.forced_pick not in script_paths:
                raise ValueError(f"Forced pick {guidelines.forced_pick} not in candidate list")
            logger.info(f"Forced pick specified: {guidelines.forced_pick}")
            return self._create_forced_result(guidelines.forced_pick, script_paths, audit_results)
        
        # Load candidates
        candidates = self._load_candidates(script_paths, audit_results)
        if not candidates:
            raise ValueError("No valid candidates (all failed to load)")
        
        # Filter by audit pass requirement
        if guidelines.require_audit_pass:
            candidates = [c for c in candidates if c.passed_audit]
            if not candidates:
                raise ValueError("No candidates passed audit (required by guidelines)")
        
        # Rank candidates
        rankings = self._rank_scripts(candidates, guidelines, dj)
        
        # Select winner (highest score)
        winner_ranking = rankings[0]
        winner_candidate = next(c for c in candidates if c.path == winner_ranking.path)
        
        # Generate selection rationale
        rationale = self._generate_selection_rationale(winner_ranking, rankings)
        
        return SelectionResult(
            winner_path=winner_ranking.path,
            winner_content=winner_candidate.content,
            rankings=rankings,
            selection_rationale=rationale
        )
    
    def _load_candidates(
        self,
        script_paths: List[Path],
        audit_results: Dict[Path, Dict[str, Any]]
    ) -> List[ScriptCandidate]:
        """Load script candidates from disk."""
        candidates = []
        for i, path in enumerate(script_paths):
            try:
                # Convert string to Path if needed
                path = Path(path)
                
                if not path.exists():
                    logger.warning(f"Script not found: {path}")
                    continue
                
                content = path.read_text(encoding='utf-8')
                audit_result = audit_results.get(path)
                
                # Infer version from filename (e.g., "julie_0.txt" -> v0, "julie_1.txt" -> v1)
                version = 0
                match = re.search(r'_(\d+)\.txt$', str(path))
                if match:
                    version = int(match.group(1))
                
                candidates.append(ScriptCandidate(
                    path=path,
                    content=content,
                    audit_result=audit_result,
                    version=version
                ))
            except Exception as e:
                logger.error(f"Failed to load {path}: {e}")
        
        return candidates
    
    def _rank_scripts(
        self,
        candidates: List[ScriptCandidate],
        guidelines: SelectionGuidelines,
        dj: Optional[str]
    ) -> List[ScriptRanking]:
        """Rank all candidates by guideline scores."""
        rankings = []
        
        for candidate in candidates:
            # Score individual guidelines
            scores = {
                "clarity": self._score_clarity(candidate, guidelines),
                "style": self._score_style(candidate, guidelines, dj),
                "creativity": self._score_creativity(candidate, guidelines),
                "conciseness": self._score_conciseness(candidate, guidelines),
                "tts_safety": self._score_tts_safety(candidate, guidelines),
                "novelty": self._score_novelty(candidate, candidates, guidelines),
            }
            
            # Compute weighted overall score
            overall = (
                scores["clarity"] * guidelines.clarity_weight +
                scores["style"] * guidelines.style_weight +
                scores["creativity"] * guidelines.creativity_weight +
                scores["conciseness"] * guidelines.conciseness_weight +
                scores["tts_safety"] * guidelines.tts_safety_weight +
                scores["novelty"] * guidelines.novelty_weight
            )
            
            # Generate rationale
            rationale = self._generate_rationale(candidate, scores, guidelines)
            
            rankings.append(ScriptRanking(
                path=candidate.path,
                overall_score=overall,
                guideline_scores=scores,
                rationale=rationale,
                rank=0  # Will be set after sorting
            ))
        
        # Sort by overall score (descending)
        rankings.sort(key=lambda r: r.overall_score, reverse=True)
        
        # Assign ranks
        for i, ranking in enumerate(rankings, 1):
            ranking.rank = i
        
        return rankings
    
    def _score_clarity(self, candidate: ScriptCandidate, guidelines: SelectionGuidelines) -> float:
        """Score clarity (grammar, readability, forbidden patterns).
        
        Returns: 0-10 score
        """
        score = 10.0
        
        # Start with audit score if available
        if candidate.audit_result:
            natural_flow = candidate.audit_result.get("criteria_scores", {}).get("natural_flow", 8.0)
            score = float(natural_flow)
        
        # Penalize forbidden patterns
        text_lower = candidate.content.lower()
        for pattern in guidelines.forbidden_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                score -= 2.0
        
        # Penalize excessive punctuation (!!!, ???, etc.)
        if re.search(r'[!?]{3,}', candidate.content):
            score -= 1.0
        
        return max(0.0, min(10.0, score))
    
    def _score_style(
        self,
        candidate: ScriptCandidate,
        guidelines: SelectionGuidelines,
        dj: Optional[str]
    ) -> float:
        """Score era/DJ style compliance.
        
        Returns: 0-10 score
        """
        score = 8.0  # Default to good
        
        # Use audit scores if available
        if candidate.audit_result:
            criteria = candidate.audit_result.get("criteria_scores", {})
            character_voice = criteria.get("character_voice", 8.0)
            era_appropriate = criteria.get("era_appropriateness", 8.0)
            score = (float(character_voice) + float(era_appropriate)) / 2.0
        
        # Additional heuristics based on DJ (if provided)
        if dj:
            text_lower = candidate.content.lower()
            dj_key = dj.lower().replace(" ", "")  # Normalize DJ name
            
            # Check for DJ-specific style markers
            if dj_key in DJ_STYLE_MARKERS:
                markers = DJ_STYLE_MARKERS[dj_key]
                if any(word in text_lower for word in markers):
                    score += 0.5
        
        return max(0.0, min(10.0, score))
    
    def _score_creativity(self, candidate: ScriptCandidate, guidelines: SelectionGuidelines) -> float:
        """Score creativity and personality.
        
        Returns: 0-10 score
        """
        score = 7.0  # Default to acceptable
        
        # Use character_voice from audit if available
        if candidate.audit_result:
            character_voice = candidate.audit_result.get("criteria_scores", {}).get("character_voice", 7.0)
            score = float(character_voice)
        
        # Bonus for variety in word choice
        words = candidate.content.split()
        unique_ratio = len(set(w.lower() for w in words)) / max(len(words), 1)
        if unique_ratio > 0.8:  # High vocabulary diversity
            score += 0.5
        
        return max(0.0, min(10.0, score))
    
    def _score_conciseness(self, candidate: ScriptCandidate, guidelines: SelectionGuidelines) -> float:
        """Score brevity and lack of filler.
        
        Returns: 0-10 score
        """
        score = 10.0
        
        # Penalize excessive length
        if len(candidate.content) > guidelines.max_length_chars:
            overage = len(candidate.content) - guidelines.max_length_chars
            score -= (overage / 100) * 2  # -2 points per 100 chars over
        
        # Use length/brevity from audit if available
        if candidate.audit_result:
            criteria = candidate.audit_result.get("criteria_scores", {})
            length_score = criteria.get("length", criteria.get("brevity", 8.0))
            score = min(score, float(length_score))
        
        # Penalize filler words
        text_lower = candidate.content.lower()
        for word in FILLER_WORDS:
            if f" {word} " in f" {text_lower} ":
                score -= 0.5
        
        return max(0.0, min(10.0, score))
    
    def _score_tts_safety(self, candidate: ScriptCandidate, guidelines: SelectionGuidelines) -> float:
        """Score TTS safety (pronunciation, synthesis-friendly phrasing).
        
        Returns: 0-10 score
        """
        score = 9.0  # Default to mostly safe
        
        text = candidate.content
        
        # Penalize complex punctuation that confuses TTS
        if '...' in text:
            score -= 0.5
        if '--' in text:
            score -= 0.5
        
        # Penalize parentheticals (TTS handles them poorly)
        if '(' in text or ')' in text:
            score -= 1.0
        
        # Penalize uncommon abbreviations
        if re.search(r'\b[A-Z]{2,}\b', text):  # All-caps words (acronyms)
            score -= 0.5
        
        # Penalize numbers (TTS can mispronounce)
        if re.search(r'\d+', text):
            score -= 0.3
        
        return max(0.0, min(10.0, score))
    
    def _score_novelty(
        self,
        candidate: ScriptCandidate,
        all_candidates: List[ScriptCandidate],
        guidelines: SelectionGuidelines
    ) -> float:
        """Score novelty (penalize near-duplicates).
        
        Returns: 0-10 score
        """
        score = 10.0
        
        # Compare with other candidates
        for other in all_candidates:
            if other.path == candidate.path:
                continue
            
            # Simple similarity check: word overlap
            words1 = set(candidate.content.lower().split())
            words2 = set(other.content.lower().split())
            
            if not words1 or not words2:
                continue
            
            overlap = len(words1 & words2) / max(len(words1), len(words2))
            
            # High overlap = penalize
            if overlap > 0.9:  # >90% similar
                score -= 3.0
            elif overlap > 0.7:  # >70% similar
                score -= 1.5
        
        return max(0.0, min(10.0, score))
    
    def _generate_rationale(
        self,
        candidate: ScriptCandidate,
        scores: Dict[str, float],
        guidelines: SelectionGuidelines
    ) -> str:
        """Generate human-readable rationale for script ranking."""
        parts = []
        
        # Audit status
        if candidate.passed_audit:
            parts.append(f"Passed audit (score: {candidate.audit_score:.1f})")
        else:
            parts.append("Failed audit")
        
        # Highlight strengths (score > 8)
        strengths = [name for name, score in scores.items() if score > 8.0]
        if strengths:
            parts.append(f"Strong: {', '.join(strengths)}")
        
        # Highlight weaknesses (score < 6)
        weaknesses = [f"{name} ({score:.1f})" for name, score in scores.items() if score < 6.0]
        if weaknesses:
            parts.append(f"Weak: {', '.join(weaknesses)}")
        
        # Version info
        if candidate.version > 0:
            parts.append(f"v{candidate.version}")
        
        return " | ".join(parts)
    
    def _generate_selection_rationale(
        self,
        winner: ScriptRanking,
        all_rankings: List[ScriptRanking]
    ) -> str:
        """Generate overall selection rationale explaining why winner was chosen."""
        parts = [f"Selected {winner.path.name} (rank #{winner.rank})"]
        
        # Overall score
        parts.append(f"Overall score: {winner.overall_score:.2f}")
        
        # Top criteria
        top_criteria = sorted(
            winner.guideline_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        top_names = [f"{name} ({score:.1f})" for name, score in top_criteria]
        parts.append(f"Top criteria: {', '.join(top_names)}")
        
        # Margin over second place
        if len(all_rankings) > 1:
            second = all_rankings[1]
            margin = winner.overall_score - second.overall_score
            parts.append(f"Margin: +{margin:.2f} over {second.path.name}")
        
        return " | ".join(parts)
    
    def _create_forced_result(
        self,
        forced_path: Path,
        all_paths: List[Path],
        audit_results: Dict[Path, Dict[str, Any]]
    ) -> SelectionResult:
        """Create result for forced pick (user override)."""
        # Load just the forced pick
        forced_path = Path(forced_path)
        content = forced_path.read_text(encoding='utf-8')
        
        # Create simple rankings (forced pick = rank 1, others unranked)
        rankings = [
            ScriptRanking(
                path=forced_path,
                overall_score=100.0,
                guideline_scores={"forced": 100.0},
                rationale="User forced pick",
                rank=1
            )
        ]
        
        # Add others as unranked
        for i, path in enumerate(all_paths, 2):
            if Path(path) == forced_path:
                continue
            rankings.append(ScriptRanking(
                path=Path(path),
                overall_score=0.0,
                guideline_scores={},
                rationale="Not selected (user override)",
                rank=i
            ))
        
        return SelectionResult(
            winner_path=forced_path,
            winner_content=content,
            rankings=rankings,
            selection_rationale=f"User forced pick: {forced_path.name}"
        )


# Convenience function for simple use cases
def pick_best_script(
    script_paths: List[Path],
    audit_results: Dict[Path, Dict[str, Any]],
    **guideline_kwargs
) -> Path:
    """Convenience function to pick best script with default guidelines.
    
    Args:
        script_paths: List of script file paths
        audit_results: Audit results for each script
        **guideline_kwargs: Optional guideline overrides (e.g., clarity_weight=2.0)
    
    Returns:
        Path to winning script
    
    Example:
        winner = pick_best_script(
            ["v0.txt", "v1.txt", "v2.txt"],
            audit_results,
            require_audit_pass=True,
            style_weight=2.0
        )
    """
    guidelines = SelectionGuidelines(**guideline_kwargs)
    picker = CherryPicker()
    result = picker.pick_best(script_paths, audit_results, guidelines)
    return result.winner_path
