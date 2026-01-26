"""Tests for AuditedGenerationAPI.

These tests verify that the audited API correctly uses staged pipeline
with automatic audit validation and retry loops.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.ai_radio.api.audited import AuditedGenerationAPI
from src.ai_radio.api.schemas import SongInfo, DJ, ContentType


@pytest.fixture
def api(tmp_path):
    """Create an AuditedGenerationAPI instance for testing."""
    return AuditedGenerationAPI(output_dir=tmp_path, test_mode=True)


@pytest.fixture
def test_song():
    """Sample song for testing."""
    return SongInfo(id="1", artist="Test Artist", title="Test Song")


@pytest.fixture(autouse=True)
def cleanup_test_files(test_song):
    """Clean up test files created in shared data directory before and after tests."""
    import shutil
    from src.ai_radio.config import GENERATED_DIR, DATA_DIR
    
    test_paths = [
        GENERATED_DIR / "intros" / "julie" / "Test_Artist-Test_Song",
        GENERATED_DIR / "outros" / "julie" / "Test_Artist-Test_Song",
        DATA_DIR / "audits" / "julie" / "Test_Artist-Test_Song",
    ]
    
    # Cleanup before test
    for path in test_paths:
        if path.exists():
            shutil.rmtree(path)
    
    yield
    
    # Cleanup after test
    for path in test_paths:
        if path.exists():
            shutil.rmtree(path)


class TestGenerateIntroWithAudit:
    """Test generate_intro_with_audit method."""
    
    def test_calls_stage_functions_in_order(self, api, test_song, tmp_path):
        """Verify stage functions are called in correct sequence."""
        with patch('src.ai_radio.api.audited.stage_generate') as mock_gen, \
             patch('src.ai_radio.api.audited.stage_audit') as mock_audit, \
             patch('src.ai_radio.api.audited.stage_regenerate') as mock_regen, \
             patch('src.ai_radio.api.audited.stage_audio') as mock_audio:
            
            # Mock audit to pass
            mock_audit.return_value = {'passed': 1, 'failed': 0}
            
            result = api.generate_intro_with_audit(
                song=test_song,
                dj=DJ.JULIE,
                max_retries=5,
                text_only=False,
            )
            
            # Verify stages called
            assert mock_gen.called
            assert mock_audit.called
            assert not mock_regen.called  # Should not regenerate if passed
            assert mock_audio.called
    
    def test_calls_regenerate_on_audit_failure(self, api, test_song, tmp_path):
        """Verify regenerate is called when audit fails."""
        with patch('src.ai_radio.api.audited.stage_generate') as mock_gen, \
             patch('src.ai_radio.api.audited.stage_audit') as mock_audit, \
             patch('src.ai_radio.api.audited.stage_regenerate') as mock_regen, \
             patch('src.ai_radio.api.audited.stage_audio') as mock_audio:
            
            # Mock audit to fail
            mock_audit.return_value = {'passed': 0, 'failed': 1}
            mock_regen.return_value = 1  # 1 item regenerated
            
            result = api.generate_intro_with_audit(
                song=test_song,
                dj=DJ.JULIE,
                max_retries=5,
                text_only=False,
            )
            
            # Verify regenerate called with max_retries
            assert mock_regen.called
            call_kwargs = mock_regen.call_args[1]
            assert call_kwargs['max_retries'] == 5
    
    def test_skips_audio_when_text_only(self, api, test_song, tmp_path):
        """Verify audio stage skipped when text_only=True."""
        with patch('src.ai_radio.api.audited.stage_generate') as mock_gen, \
             patch('src.ai_radio.api.audited.stage_audit') as mock_audit, \
             patch('src.ai_radio.api.audited.stage_regenerate') as mock_regen, \
             patch('src.ai_radio.api.audited.stage_audio') as mock_audio:
            
            # Mock audit to pass
            mock_audit.return_value = {'passed': 1, 'failed': 0}
            
            result = api.generate_intro_with_audit(
                song=test_song,
                dj=DJ.JULIE,
                max_retries=5,
                text_only=True,  # Skip audio
            )
            
            # Verify audio not called
            assert not mock_audio.called
    
    def test_passes_single_item_lists_to_stages(self, api, test_song, tmp_path):
        """Verify stages receive single-item lists as expected."""
        with patch('src.ai_radio.api.audited.stage_generate') as mock_gen, \
             patch('src.ai_radio.api.audited.stage_audit') as mock_audit, \
             patch('src.ai_radio.api.audited.stage_audio') as mock_audio:
            
            # Mock audit to pass
            mock_audit.return_value = {'passed': 1, 'failed': 0}
            
            result = api.generate_intro_with_audit(
                song=test_song,
                dj=DJ.JULIE,
                max_retries=5,
                text_only=False,
            )
            
            # Verify generate received single-item lists
            gen_kwargs = mock_gen.call_args[1]
            assert gen_kwargs['songs'] == [test_song.to_dict()]
            assert gen_kwargs['djs'] == ['julie']
            
            # Verify audit received single-item lists
            audit_kwargs = mock_audit.call_args[1]
            assert audit_kwargs['songs'] == [test_song.to_dict()]
            assert audit_kwargs['djs'] == ['julie']
    
    def test_returns_result_with_audit_info(self, api, test_song, tmp_path):
        """Verify result includes audit status."""
        # Create script and audit files
        from src.ai_radio.core.paths import get_script_path, get_audit_path
        import json
        
        script_path = get_script_path(test_song.to_dict(), 'julie', 'intros')
        script_path.parent.mkdir(parents=True, exist_ok=True)
        script_path.write_text("Test intro script")
        
        audit_path = get_audit_path(test_song.to_dict(), 'julie', True, 'song_intro')
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        audit_path.write_text(json.dumps({'score': 85, 'passed': True}))
        
        with patch('src.ai_radio.api.audited.stage_generate'), \
             patch('src.ai_radio.api.audited.stage_audit') as mock_audit, \
             patch('src.ai_radio.api.audited.stage_audio'):
            
            mock_audit.return_value = {'passed': 1, 'failed': 0}
            
            result = api.generate_intro_with_audit(
                song=test_song,
                dj=DJ.JULIE,
                max_retries=5,
                text_only=True,
            )
            
            # Verify result has audit info
            assert result.success
            assert result.audit_passed is True
            assert result.audit_score == 85
    
    def test_handles_exceptions_gracefully(self, api, test_song, tmp_path):
        """Verify exceptions are caught and returned as failed results."""
        with patch('src.ai_radio.api.audited.stage_generate') as mock_gen:
            mock_gen.side_effect = Exception("Test error")
            
            result = api.generate_intro_with_audit(
                song=test_song,
                dj=DJ.JULIE,
                max_retries=5,
                text_only=True,
            )
            
            # Verify error result
            assert not result.success
            assert "Test error" in result.error


class TestBuildResultFromStages:
    """Test _build_result_from_stages helper."""
    
    def test_reads_passed_audit_result(self, test_song, tmp_path):
        """Verify reads audit result when passed."""
        # Use tmp_path as output dir to avoid test interference
        api = AuditedGenerationAPI(output_dir=tmp_path, test_mode=True)
        from src.ai_radio.core.paths import get_script_path, get_audit_path
        import json
        
        # Create files
        script_path = get_script_path(test_song.to_dict(), 'julie', 'intros')
        script_path.parent.mkdir(parents=True, exist_ok=True)
        script_path.write_text("Test script")
        
        audit_path = get_audit_path(test_song.to_dict(), 'julie', True, 'song_intro')
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        audit_path.write_text(json.dumps({'score': 90, 'passed': True}))
        
        result = api._build_result_from_stages(test_song, DJ.JULIE, ContentType.INTRO)
        
        assert result.success
        assert result.audit_passed is True
        assert result.audit_score == 90
        assert result.text == "Test script"
    
    def test_reads_failed_audit_result(self, test_song, tmp_path):
        """Verify reads audit result when failed."""
        # Use tmp_path as output dir to avoid test interference
        api = AuditedGenerationAPI(output_dir=tmp_path, test_mode=True)
        from src.ai_radio.core.paths import get_script_path, get_audit_path
        import json
        
        # Create files
        script_path = get_script_path(test_song.to_dict(), 'julie', 'intros')
        script_path.parent.mkdir(parents=True, exist_ok=True)
        script_path.write_text("Test script")
        
        audit_path = get_audit_path(test_song.to_dict(), 'julie', False, 'song_intro')
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        audit_path.write_text(json.dumps({'score': 45, 'passed': False}))
        
        result = api._build_result_from_stages(test_song, DJ.JULIE, ContentType.INTRO)
        
        assert result.success  # Script exists
        assert result.audit_passed is False
        assert result.audit_score == 45
    
    def test_handles_missing_audit_file(self, test_song, tmp_path):
        """Verify handles case where audit file doesn't exist."""
        # Use tmp_path as output dir to avoid test interference
        api = AuditedGenerationAPI(output_dir=tmp_path, test_mode=True)
        from src.ai_radio.core.paths import get_script_path
        
        # Create only script
        script_path = get_script_path(test_song.to_dict(), 'julie', 'intros')
        script_path.parent.mkdir(parents=True, exist_ok=True)
        script_path.write_text("Test script")
        
        result = api._build_result_from_stages(test_song, DJ.JULIE, ContentType.INTRO)
        
        assert result.success
        assert result.audit_passed is None
        assert result.audit_score is None
