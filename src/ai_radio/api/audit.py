"""Audit API for script quality evaluation.

This module provides functions to run audits, fetch audit results,
and manage the audit workflow programmatically.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from src.ai_radio.config import DATA_DIR, WEATHER_TIMES
from src.ai_radio.generation.auditor import audit_script
from src.ai_radio.generation.llm_client import LLMClient
from src.ai_radio.core.paths import (
    get_script_path,
    get_audit_path,
    get_time_script_path,
    get_time_audit_path,
    get_weather_script_path,
    get_weather_audit_path,
)
from src.ai_radio.api.schemas import (
    AuditResult,
    AuditFilter,
    ContentType,
    DJ,
    SongInfo,
    AuditStatus,
)
from src.ai_radio.stages.utils import FakeAuditorClient

logger = logging.getLogger(__name__)


class AuditAPI:
    """API for script auditing and result management.
    
    Provides methods to run audits on scripts, fetch audit results,
    and query the audit database.
    
    Example:
        api = AuditAPI()
        
        # Run an audit
        result = api.audit_script(
            content_type=ContentType.INTRO,
            dj=DJ.JULIE,
            song=SongInfo(id="1", artist="Johnny Cash", title="Ring of Fire")
        )
        
        # List failed audits
        failed = api.list_audit_results(passed=False)
    """
    
    def __init__(
        self,
        data_dir: Optional[Path] = None,
        test_mode: bool = False,
    ):
        """Initialize the Audit API.
        
        Args:
            data_dir: Override for data directory (default: config.DATA_DIR)
            test_mode: If True, use fake auditor (no LLM calls)
        """
        self.data_dir = data_dir or DATA_DIR
        self.test_mode = test_mode
        self._client = None
    
    @property
    def client(self):
        """Get or create the audit client."""
        if self._client is None:
            if self.test_mode:
                self._client = FakeAuditorClient()
            else:
                self._client = LLMClient(model="dolphin-llama3")
        return self._client
    
    def audit_script(
        self,
        content_type: ContentType,
        dj: DJ,
        song: Optional[SongInfo] = None,
        hour: Optional[int] = None,
        minute: Optional[int] = None,
        script_text: Optional[str] = None,
        save_result: bool = True,
    ) -> AuditResult:
        """Run an audit on a specific script.
        
        Args:
            content_type: Type of content being audited
            dj: DJ personality
            song: Song info (required for INTRO/OUTRO)
            hour: Hour (required for TIME/WEATHER)
            minute: Minute (required for TIME)
            script_text: Script text to audit (if not provided, reads from file)
            save_result: If True, save result to disk
            
        Returns:
            AuditResult with pass/fail status and scores
        """
        # Determine script path and load text
        if content_type == ContentType.INTRO:
            if song is None:
                raise ValueError("song is required for INTRO content type")
            script_path = get_script_path(song.to_dict(), dj.value, content_type='intros')
            script_id = f"{song.id}_{dj.value}_intro"
            audit_content_type = "song_intro"
        elif content_type == ContentType.OUTRO:
            if song is None:
                raise ValueError("song is required for OUTRO content type")
            script_path = get_script_path(song.to_dict(), dj.value, content_type='outros')
            script_id = f"{song.id}_{dj.value}_outro"
            audit_content_type = "song_outro"
        elif content_type == ContentType.TIME:
            if hour is None or minute is None:
                raise ValueError("hour and minute are required for TIME content type")
            script_path = get_time_script_path(hour, minute, dj.value)
            time_id = f"{hour:02d}-{minute:02d}"
            script_id = f"{time_id}_{dj.value}_time"
            audit_content_type = "time_announcement"
        elif content_type == ContentType.WEATHER:
            if hour is None:
                raise ValueError("hour is required for WEATHER content type")
            script_path = get_weather_script_path(hour, dj.value)
            time_id = f"{hour:02d}-00"
            script_id = f"{time_id}_{dj.value}_weather"
            audit_content_type = "weather_announcement"
        else:
            raise ValueError(f"Unknown content type: {content_type}")
        
        # Get script text
        if script_text is None:
            if not script_path.exists():
                raise FileNotFoundError(f"Script not found: {script_path}")
            script_text = script_path.read_text(encoding='utf-8')
        
        # Run the audit
        try:
            result = audit_script(
                client=self.client,
                script_content=script_text,
                script_id=script_id,
                dj=dj.value,
                content_type=audit_content_type,
            )
            
            # Determine audit path
            if content_type == ContentType.INTRO or content_type == ContentType.OUTRO:
                audit_path = get_audit_path(song.to_dict(), dj.value, passed=result.passed, content_type=audit_content_type)
            elif content_type == ContentType.TIME:
                audit_path = get_time_audit_path(hour, minute, dj.value, passed=result.passed)
            else:  # WEATHER
                audit_path = get_weather_audit_path(hour, dj.value, passed=result.passed)
            
            # Save result if requested
            if save_result:
                audit_path.parent.mkdir(parents=True, exist_ok=True)
                with open(audit_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        "script_id": result.script_id,
                        "dj": result.dj,
                        "content_type": result.content_type,
                        "score": result.score,
                        "passed": result.passed,
                        "criteria_scores": result.criteria_scores,
                        "issues": result.issues,
                        "notes": result.notes,
                        "audited_at": datetime.now().isoformat(),
                    }, f, indent=2, ensure_ascii=False)
            
            # Convert to API schema
            return AuditResult(
                script_id=result.script_id,
                dj=dj,
                content_type=content_type,
                passed=result.passed,
                score=result.score,
                criteria_scores=result.criteria_scores,
                issues=result.issues,
                notes=result.notes,
                audit_path=audit_path,
                audited_at=datetime.now(),
            )
            
        except Exception as e:
            logger.error(f"Audit failed for {script_id}: {e}")
            raise
    
    def list_audit_results(
        self,
        dj: Optional[DJ] = None,
        passed: Optional[bool] = None,
        content_type: Optional[ContentType] = None,
    ) -> List[AuditResult]:
        """List audit results matching the given filters.
        
        Args:
            dj: Filter by DJ (None for all)
            passed: Filter by pass/fail status (None for all)
            content_type: Filter by content type (None for all)
            
        Returns:
            List of AuditResult objects
        """
        results = []
        djs = [dj] if dj else [DJ.JULIE, DJ.MR_NEW_VEGAS]
        statuses = [passed] if passed is not None else [True, False]
        
        audit_dir = self.data_dir / "audit"
        
        for d in djs:
            dj_dir = audit_dir / d.value
            if not dj_dir.exists():
                continue
            
            for status in statuses:
                status_folder = "passed" if status else "failed"
                status_dir = dj_dir / status_folder
                
                if not status_dir.exists():
                    continue
                
                for audit_file in status_dir.glob("*.json"):
                    try:
                        with open(audit_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        audit_result = AuditResult.from_dict(data, audit_path=audit_file)
                        
                        # Apply content type filter
                        if content_type is not None:
                            if audit_result.content_type != content_type:
                                continue
                        
                        results.append(audit_result)
                    except Exception as e:
                        logger.warning(f"Error loading audit result {audit_file}: {e}")
        
        return results
    
    def get_audit_result(
        self,
        content_type: ContentType,
        dj: DJ,
        song: Optional[SongInfo] = None,
        hour: Optional[int] = None,
        minute: Optional[int] = None,
    ) -> Optional[AuditResult]:
        """Get the audit result for a specific script.
        
        Args:
            content_type: Type of content
            dj: DJ personality
            song: Song info (required for INTRO/OUTRO)
            hour: Hour (required for TIME/WEATHER)
            minute: Minute (required for TIME)
            
        Returns:
            AuditResult if found, None otherwise
        """
        # Check both passed and failed paths
        for passed in [True, False]:
            if content_type == ContentType.INTRO:
                if song is None:
                    return None
                audit_path = get_audit_path(song.to_dict(), dj.value, passed=passed, content_type='song_intro')
            elif content_type == ContentType.OUTRO:
                if song is None:
                    return None
                audit_path = get_audit_path(song.to_dict(), dj.value, passed=passed, content_type='song_outro')
            elif content_type == ContentType.TIME:
                if hour is None or minute is None:
                    return None
                audit_path = get_time_audit_path(hour, minute, dj.value, passed=passed)
            elif content_type == ContentType.WEATHER:
                if hour is None:
                    return None
                audit_path = get_weather_audit_path(hour, dj.value, passed=passed)
            else:
                return None
            
            if audit_path.exists():
                try:
                    with open(audit_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    return AuditResult.from_dict(data, audit_path=audit_path)
                except Exception as e:
                    logger.warning(f"Error loading audit result {audit_path}: {e}")
        
        return None
    
    def get_audit_summary(self, dj: Optional[DJ] = None) -> dict:
        """Get a summary of audit results.
        
        Args:
            dj: Filter by DJ (None for all)
            
        Returns:
            Dictionary with counts and pass rates
        """
        passed_results = self.list_audit_results(dj=dj, passed=True)
        failed_results = self.list_audit_results(dj=dj, passed=False)
        
        total = len(passed_results) + len(failed_results)
        pass_rate = len(passed_results) / total if total > 0 else 0.0
        
        # Group by content type
        by_type = {}
        for ct in ContentType:
            ct_passed = sum(1 for r in passed_results if r.content_type == ct)
            ct_failed = sum(1 for r in failed_results if r.content_type == ct)
            ct_total = ct_passed + ct_failed
            by_type[ct.value] = {
                "passed": ct_passed,
                "failed": ct_failed,
                "total": ct_total,
                "pass_rate": ct_passed / ct_total if ct_total > 0 else 0.0,
            }
        
        return {
            "total": total,
            "passed": len(passed_results),
            "failed": len(failed_results),
            "pass_rate": pass_rate,
            "by_content_type": by_type,
        }
    
    def delete_audit_result(
        self,
        content_type: ContentType,
        dj: DJ,
        song: Optional[SongInfo] = None,
        hour: Optional[int] = None,
        minute: Optional[int] = None,
    ) -> bool:
        """Delete an audit result (for re-auditing).
        
        Args:
            content_type: Type of content
            dj: DJ personality
            song: Song info (required for INTRO/OUTRO)
            hour: Hour (required for TIME/WEATHER)
            minute: Minute (required for TIME)
            
        Returns:
            True if deleted, False if not found
        """
        # Check both passed and failed paths
        for passed in [True, False]:
            if content_type == ContentType.INTRO:
                audit_path = get_audit_path(song.to_dict(), dj.value, passed=passed, content_type='song_intro')
            elif content_type == ContentType.OUTRO:
                audit_path = get_audit_path(song.to_dict(), dj.value, passed=passed, content_type='song_outro')
            elif content_type == ContentType.TIME:
                audit_path = get_time_audit_path(hour, minute, dj.value, passed=passed)
            elif content_type == ContentType.WEATHER:
                audit_path = get_weather_audit_path(hour, dj.value, passed=passed)
            else:
                return False
            
            if audit_path.exists():
                audit_path.unlink()
                logger.info(f"Deleted audit result: {audit_path}")
                return True
        
        return False
