"""Tests for cherry_picker module."""
import pytest
import json
from pathlib import Path
from src.ai_radio.cherry_picker import (
    CherryPicker,
    ScriptCandidate,
    SelectionGuidelines,
    ScriptRanking,
    SelectionResult,
    pick_best_script,
)


class TestScriptCandidate:
    """Test ScriptCandidate dataclass."""
    
    def test_passed_audit_property(self):
        """Should correctly determine audit pass/fail."""
        # Passed
        candidate = ScriptCandidate(
            path=Path("test.txt"),
            content="Test content",
            audit_result={"passed": True, "score": 8.0}
        )
        assert candidate.passed_audit is True
        
        # Failed
        candidate = ScriptCandidate(
            path=Path("test.txt"),
            content="Test content",
            audit_result={"passed": False, "score": 4.0}
        )
        assert candidate.passed_audit is False
        
        # No audit
        candidate = ScriptCandidate(
            path=Path("test.txt"),
            content="Test content",
            audit_result=None
        )
        assert candidate.passed_audit is False
    
    def test_audit_score_property(self):
        """Should extract audit score."""
        candidate = ScriptCandidate(
            path=Path("test.txt"),
            content="Test content",
            audit_result={"score": 7.5}
        )
        assert candidate.audit_score == 7.5
        
        # No audit
        candidate = ScriptCandidate(
            path=Path("test.txt"),
            content="Test content",
            audit_result=None
        )
        assert candidate.audit_score == 0.0
    
    def test_audit_issues_property(self):
        """Should extract audit issues."""
        candidate = ScriptCandidate(
            path=Path("test.txt"),
            content="Test content",
            audit_result={"issues": ["Issue 1", "Issue 2"]}
        )
        assert candidate.audit_issues == ["Issue 1", "Issue 2"]
        
        # No audit
        candidate = ScriptCandidate(
            path=Path("test.txt"),
            content="Test content",
            audit_result=None
        )
        assert candidate.audit_issues == []


class TestSelectionGuidelines:
    """Test SelectionGuidelines dataclass."""
    
    def test_default_values(self):
        """Should have sensible defaults."""
        guidelines = SelectionGuidelines()
        assert guidelines.require_audit_pass is True
        assert guidelines.clarity_weight == 1.0
        assert guidelines.style_weight == 1.5
        assert guidelines.creativity_weight == 1.2
        assert guidelines.forced_pick is None
    
    def test_custom_values(self):
        """Should accept custom values."""
        guidelines = SelectionGuidelines(
            require_audit_pass=False,
            clarity_weight=2.0,
            forced_pick=Path("forced.txt")
        )
        assert guidelines.require_audit_pass is False
        assert guidelines.clarity_weight == 2.0
        assert guidelines.forced_pick == Path("forced.txt")


class TestCherryPickerBasicSelection:
    """Test basic selection functionality."""
    
    def test_selects_single_script(self, tmp_path):
        """Should handle single script case."""
        # Create single script
        script = tmp_path / "script.txt"
        script.write_text("Good script content")
        
        audit_results = {
            script: {
                "passed": True,
                "score": 8.0,
                "criteria_scores": {
                    "character_voice": 8.0,
                    "natural_flow": 8.0
                },
                "issues": [],
                "notes": "Good"
            }
        }
        
        picker = CherryPicker()
        result = picker.pick_best([script], audit_results)
        
        assert result.winner_path == script
        assert len(result.rankings) == 1
        assert result.rankings[0].rank == 1
    
    def test_selects_best_from_multiple(self, tmp_path):
        """Should select best script from batch."""
        # Create scripts
        script1 = tmp_path / "v0.txt"
        script1.write_text("This is a good script")
        
        script2 = tmp_path / "v1.txt"
        script2.write_text("This is an excellent script with better content")
        
        script3 = tmp_path / "v2.txt"
        script3.write_text("This is okay")
        
        audit_results = {
            script1: {"passed": True, "score": 7.0, "criteria_scores": {"character_voice": 7.0, "natural_flow": 7.0}},
            script2: {"passed": True, "score": 9.0, "criteria_scores": {"character_voice": 9.0, "natural_flow": 9.0}},
            script3: {"passed": True, "score": 6.0, "criteria_scores": {"character_voice": 6.0, "natural_flow": 6.0}},
        }
        
        picker = CherryPicker()
        result = picker.pick_best([script1, script2, script3], audit_results)
        
        # Should select v1 (highest score)
        assert result.winner_path == script2
        assert len(result.rankings) == 3
        assert result.rankings[0].path == script2  # Rank 1
        assert result.rankings[0].rank == 1
        assert result.rankings[1].rank == 2
        assert result.rankings[2].rank == 3
    
    def test_filters_by_audit_pass(self, tmp_path):
        """Should filter out failed audits when required."""
        script1 = tmp_path / "v0.txt"
        script1.write_text("Failed script")
        
        script2 = tmp_path / "v1.txt"
        script2.write_text("Passed script")
        
        audit_results = {
            script1: {"passed": False, "score": 4.0, "criteria_scores": {}, "issues": ["Bad"]},
            script2: {"passed": True, "score": 8.0, "criteria_scores": {"character_voice": 8.0}},
        }
        
        picker = CherryPicker()
        guidelines = SelectionGuidelines(require_audit_pass=True)
        result = picker.pick_best([script1, script2], audit_results, guidelines)
        
        # Should only consider v1
        assert result.winner_path == script2
        assert len(result.rankings) == 1
    
    def test_includes_failed_when_not_required(self, tmp_path):
        """Should include failed audits when not required."""
        script1 = tmp_path / "v0.txt"
        script1.write_text("Failed script")
        
        script2 = tmp_path / "v1.txt"
        script2.write_text("Passed script")
        
        audit_results = {
            script1: {"passed": False, "score": 4.0, "criteria_scores": {"character_voice": 4.0}},
            script2: {"passed": True, "score": 8.0, "criteria_scores": {"character_voice": 8.0}},
        }
        
        picker = CherryPicker()
        guidelines = SelectionGuidelines(require_audit_pass=False)
        result = picker.pick_best([script1, script2], audit_results, guidelines)
        
        # Should consider both, pick v1
        assert result.winner_path == script2
        assert len(result.rankings) == 2
    
    def test_raises_on_empty_list(self):
        """Should raise error on empty script list."""
        picker = CherryPicker()
        with pytest.raises(ValueError, match="No script paths provided"):
            picker.pick_best([], {})
    
    def test_raises_when_no_pass(self, tmp_path):
        """Should raise error when all scripts fail and pass required."""
        script = tmp_path / "v0.txt"
        script.write_text("Failed script")
        
        audit_results = {
            script: {"passed": False, "score": 3.0, "criteria_scores": {}}
        }
        
        picker = CherryPicker()
        guidelines = SelectionGuidelines(require_audit_pass=True)
        
        with pytest.raises(ValueError, match="No candidates passed audit"):
            picker.pick_best([script], audit_results, guidelines)


class TestGuidelineScoring:
    """Test individual guideline scoring functions."""
    
    def test_clarity_scoring(self, tmp_path):
        """Should score clarity based on natural flow and forbidden patterns."""
        picker = CherryPicker()
        guidelines = SelectionGuidelines()
        
        # Good clarity
        candidate = ScriptCandidate(
            path=tmp_path / "good.txt",
            content="This is a well-written script.",
            audit_result={"criteria_scores": {"natural_flow": 9.0}}
        )
        score = picker._score_clarity(candidate, guidelines)
        assert score >= 8.0
        
        # Bad clarity (forbidden pattern)
        candidate = ScriptCandidate(
            path=tmp_path / "bad.txt",
            content="This is awesome and cool!",
            audit_result={"criteria_scores": {"natural_flow": 8.0}}
        )
        score = picker._score_clarity(candidate, guidelines)
        assert score < 8.0  # Penalized for "awesome" and "cool"
        
        # Excessive punctuation
        candidate = ScriptCandidate(
            path=tmp_path / "punctuation.txt",
            content="This is amazing!!!",
            audit_result={"criteria_scores": {"natural_flow": 8.0}}
        )
        score = picker._score_clarity(candidate, guidelines)
        assert score < 8.0  # Penalized for !!!
    
    def test_style_scoring(self, tmp_path):
        """Should score style based on era appropriateness and character voice."""
        picker = CherryPicker()
        guidelines = SelectionGuidelines()
        
        # Good style
        candidate = ScriptCandidate(
            path=tmp_path / "good.txt",
            content="Greetings, friends and neighbors.",
            audit_result={
                "criteria_scores": {
                    "character_voice": 9.0,
                    "era_appropriateness": 9.0
                }
            }
        )
        score = picker._score_style(candidate, guidelines, dj="julie")
        assert score >= 8.0
        
        # Julie-specific bonus
        candidate_julie = ScriptCandidate(
            path=tmp_path / "julie.txt",
            content="Welcome home, friends.",
            audit_result={
                "criteria_scores": {
                    "character_voice": 8.0,
                    "era_appropriateness": 8.0
                }
            }
        )
        score_julie = picker._score_style(candidate_julie, guidelines, dj="julie")
        assert score_julie > 8.0  # Bonus for "friends" and "home"
        
        # Mr. New Vegas bonus
        candidate_mnv = ScriptCandidate(
            path=tmp_path / "mnv.txt",
            content="A lovely evening in the wasteland.",
            audit_result={
                "criteria_scores": {
                    "character_voice": 8.0,
                    "era_appropriateness": 8.0
                }
            }
        )
        score_mnv = picker._score_style(candidate_mnv, guidelines, dj="mr. new vegas")
        assert score_mnv > 8.0  # Bonus for "lovely"
    
    def test_conciseness_scoring(self, tmp_path):
        """Should score conciseness based on length and filler."""
        picker = CherryPicker()
        guidelines = SelectionGuidelines(max_length_chars=100)
        
        # Concise
        candidate = ScriptCandidate(
            path=tmp_path / "concise.txt",
            content="Brief and to the point.",
            audit_result={"criteria_scores": {"length": 9.0}}
        )
        score = picker._score_conciseness(candidate, guidelines)
        assert score >= 9.0
        
        # Too long
        candidate = ScriptCandidate(
            path=tmp_path / "long.txt",
            content="x" * 250,  # 250 chars
            audit_result={"criteria_scores": {"length": 8.0}}
        )
        score = picker._score_conciseness(candidate, guidelines)
        assert score < 8.0  # Penalized for length
        
        # Filler words
        candidate = ScriptCandidate(
            path=tmp_path / "filler.txt",
            content="So basically you know this is like actually good.",
            audit_result={"criteria_scores": {"length": 8.0}}
        )
        score = picker._score_conciseness(candidate, guidelines)
        assert score < 8.0  # Penalized for filler
    
    def test_tts_safety_scoring(self, tmp_path):
        """Should score TTS safety based on pronunciation-friendly features."""
        picker = CherryPicker()
        guidelines = SelectionGuidelines()
        
        # Safe
        candidate = ScriptCandidate(
            path=tmp_path / "safe.txt",
            content="This is a simple, clear sentence.",
            audit_result={}
        )
        score = picker._score_tts_safety(candidate, guidelines)
        assert score >= 8.0
        
        # Unsafe (parentheticals, ellipsis)
        candidate = ScriptCandidate(
            path=tmp_path / "unsafe.txt",
            content="This is... (you know) a bit tricky.",
            audit_result={}
        )
        score = picker._score_tts_safety(candidate, guidelines)
        assert score < 9.0  # Penalized
        
        # Numbers and acronyms
        candidate = ScriptCandidate(
            path=tmp_path / "numbers.txt",
            content="The year 2024 with the FBI and CIA.",
            audit_result={}
        )
        score = picker._score_tts_safety(candidate, guidelines)
        assert score < 9.0  # Penalized
    
    def test_novelty_scoring(self, tmp_path):
        """Should penalize near-duplicates."""
        picker = CherryPicker()
        guidelines = SelectionGuidelines()
        
        candidate1 = ScriptCandidate(
            path=tmp_path / "v0.txt",
            content="This is a unique script about music.",
            audit_result={}
        )
        
        candidate2 = ScriptCandidate(
            path=tmp_path / "v1.txt",
            content="This is a unique script about music.",  # Duplicate
            audit_result={}
        )
        
        candidate3 = ScriptCandidate(
            path=tmp_path / "v2.txt",
            content="Completely different content here.",
            audit_result={}
        )
        
        candidates = [candidate1, candidate2, candidate3]
        
        # candidate1 vs duplicate should have low novelty
        score1 = picker._score_novelty(candidate1, candidates, guidelines)
        assert score1 < 8.0
        
        # candidate3 (unique) should have high novelty
        score3 = picker._score_novelty(candidate3, candidates, guidelines)
        assert score3 >= 9.0


class TestForcedPick:
    """Test forced pick (user override) functionality."""
    
    def test_forced_pick_wins(self, tmp_path):
        """Should select forced pick regardless of scores."""
        script1 = tmp_path / "v0.txt"
        script1.write_text("Excellent script")
        
        script2 = tmp_path / "v1.txt"
        script2.write_text("Bad script")
        
        audit_results = {
            script1: {"passed": True, "score": 9.0, "criteria_scores": {"character_voice": 9.0}},
            script2: {"passed": False, "score": 3.0, "criteria_scores": {"character_voice": 3.0}},
        }
        
        picker = CherryPicker()
        guidelines = SelectionGuidelines(forced_pick=script2)
        result = picker.pick_best([script1, script2], audit_results, guidelines)
        
        # Should select v1 despite lower score
        assert result.winner_path == script2
        assert "forced pick" in result.selection_rationale.lower()
    
    def test_forced_pick_not_in_list_raises(self, tmp_path):
        """Should raise error if forced pick not in candidate list."""
        script1 = tmp_path / "v0.txt"
        script1.write_text("Script")
        
        script2 = tmp_path / "v1.txt"
        script2.write_text("Other")
        
        audit_results = {script1: {"passed": True, "score": 8.0, "criteria_scores": {}}}
        
        picker = CherryPicker()
        guidelines = SelectionGuidelines(forced_pick=script2)  # Not in list
        
        with pytest.raises(ValueError, match="Forced pick.*not in candidate list"):
            picker.pick_best([script1], audit_results, guidelines)


class TestRankingAndRationale:
    """Test ranking and rationale generation."""
    
    def test_rankings_ordered_by_score(self, tmp_path):
        """Should rank scripts by overall score."""
        scripts = [tmp_path / f"v{i}.txt" for i in range(3)]
        for script in scripts:
            script.write_text("Content")
        
        audit_results = {
            scripts[0]: {"passed": True, "score": 6.0, "criteria_scores": {"character_voice": 6.0, "natural_flow": 6.0}},
            scripts[1]: {"passed": True, "score": 9.0, "criteria_scores": {"character_voice": 9.0, "natural_flow": 9.0}},
            scripts[2]: {"passed": True, "score": 7.5, "criteria_scores": {"character_voice": 7.5, "natural_flow": 7.5}},
        }
        
        picker = CherryPicker()
        result = picker.pick_best(scripts, audit_results)
        
        # Should be ranked: v1 (9.0), v2 (7.5), v0 (6.0)
        assert result.rankings[0].path == scripts[1]
        assert result.rankings[1].path == scripts[2]
        assert result.rankings[2].path == scripts[0]
        
        assert result.rankings[0].rank == 1
        assert result.rankings[1].rank == 2
        assert result.rankings[2].rank == 3
    
    def test_rationale_includes_key_info(self, tmp_path):
        """Should generate informative rationale."""
        script = tmp_path / "test.txt"
        script.write_text("Good content")
        
        audit_results = {
            script: {
                "passed": True,
                "score": 8.5,
                "criteria_scores": {"character_voice": 9.0, "natural_flow": 8.0}
            }
        }
        
        picker = CherryPicker()
        result = picker.pick_best([script], audit_results)
        
        rationale = result.rankings[0].rationale
        assert "Passed audit" in rationale
        assert "8.5" in rationale
        
        selection_rationale = result.selection_rationale
        assert "rank" in selection_rationale.lower()
        assert "score" in selection_rationale.lower()


class TestWeightConfiguration:
    """Test guideline weight configuration."""
    
    def test_weights_affect_selection(self, tmp_path):
        """Should respect guideline weights in selection."""
        # Script 1: High clarity, low style
        script1 = tmp_path / "v0.txt"
        script1.write_text("Clear but generic script.")
        
        # Script 2: Low clarity, high style
        script2 = tmp_path / "v1.txt"
        script2.write_text("Greetings, dear friends and neighbors of Appalachia!")
        
        audit_results = {
            script1: {
                "passed": True,
                "score": 8.0,
                "criteria_scores": {
                    "natural_flow": 9.0,
                    "character_voice": 6.0,
                    "era_appropriateness": 6.0
                }
            },
            script2: {
                "passed": True,
                "score": 7.0,
                "criteria_scores": {
                    "natural_flow": 6.0,
                    "character_voice": 9.0,
                    "era_appropriateness": 9.0
                }
            },
        }
        
        picker = CherryPicker()
        
        # High clarity weight -> script1 wins
        guidelines_clarity = SelectionGuidelines(clarity_weight=5.0, style_weight=1.0)
        result1 = picker.pick_best([script1, script2], audit_results, guidelines_clarity, dj="julie")
        assert result1.winner_path == script1
        
        # High style weight -> script2 wins
        guidelines_style = SelectionGuidelines(clarity_weight=1.0, style_weight=5.0)
        result2 = picker.pick_best([script1, script2], audit_results, guidelines_style, dj="julie")
        assert result2.winner_path == script2


class TestConvenienceFunction:
    """Test convenience function."""
    
    def test_pick_best_script_convenience(self, tmp_path):
        """Should provide simple interface for common use case."""
        script1 = tmp_path / "v0.txt"
        script1.write_text("Script 1")
        
        script2 = tmp_path / "v1.txt"
        script2.write_text("Script 2")
        
        audit_results = {
            script1: {"passed": True, "score": 7.0, "criteria_scores": {"character_voice": 7.0}},
            script2: {"passed": True, "score": 9.0, "criteria_scores": {"character_voice": 9.0}},
        }
        
        winner = pick_best_script([script1, script2], audit_results)
        
        assert winner == script2
    
    def test_convenience_accepts_kwargs(self, tmp_path):
        """Should accept guideline kwargs."""
        script1 = tmp_path / "v0.txt"
        script1.write_text("Script")
        
        script2 = tmp_path / "v1.txt"
        script2.write_text("Other")
        
        audit_results = {
            script1: {"passed": True, "score": 8.0, "criteria_scores": {}},
            script2: {"passed": False, "score": 4.0, "criteria_scores": {}},
        }
        
        # Allow failed audits
        winner = pick_best_script(
            [script1, script2],
            audit_results,
            require_audit_pass=False
        )
        
        assert winner == script1


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_missing_script_file(self, tmp_path):
        """Should handle missing script files gracefully."""
        script1 = tmp_path / "exists.txt"
        script1.write_text("Content")
        
        script2 = tmp_path / "missing.txt"  # Not created
        
        audit_results = {
            script1: {"passed": True, "score": 8.0, "criteria_scores": {}},
            script2: {"passed": True, "score": 9.0, "criteria_scores": {}},
        }
        
        picker = CherryPicker()
        result = picker.pick_best([script1, script2], audit_results)
        
        # Should only consider script1
        assert result.winner_path == script1
        assert len(result.rankings) == 1
    
    def test_missing_audit_result(self, tmp_path):
        """Should handle missing audit results."""
        script = tmp_path / "script.txt"
        script.write_text("Content")
        
        audit_results = {}  # No audit for this script
        
        picker = CherryPicker()
        guidelines = SelectionGuidelines(require_audit_pass=False)
        result = picker.pick_best([script], audit_results, guidelines)
        
        # Should still process (with default scores)
        assert result.winner_path == script
    
    def test_incomplete_audit_result(self, tmp_path):
        """Should handle incomplete audit results."""
        script = tmp_path / "script.txt"
        script.write_text("Content")
        
        audit_results = {
            script: {
                "passed": True,
                # Missing score, criteria_scores, etc.
            }
        }
        
        picker = CherryPicker()
        result = picker.pick_best([script], audit_results)
        
        # Should not crash
        assert result.winner_path == script
    
    def test_tie_handling(self, tmp_path):
        """Should handle ties consistently."""
        script1 = tmp_path / "v0.txt"
        script1.write_text("Identical content")
        
        script2 = tmp_path / "v1.txt"
        script2.write_text("Identical content")
        
        audit_results = {
            script1: {"passed": True, "score": 8.0, "criteria_scores": {"character_voice": 8.0}},
            script2: {"passed": True, "score": 8.0, "criteria_scores": {"character_voice": 8.0}},
        }
        
        picker = CherryPicker()
        result = picker.pick_best([script1, script2], audit_results)
        
        # Should pick one (first in list after sort is stable)
        assert result.winner_path in [script1, script2]
        assert len(result.rankings) == 2
