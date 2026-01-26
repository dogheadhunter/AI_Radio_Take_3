"""Review queue API for human-in-the-loop approval workflow.

This module provides functions to manage the review queue for
approving/rejecting generated scripts and triggering regeneration.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from src.ai_radio.config import DATA_DIR, GENERATED_DIR
from src.ai_radio.core.paths import (
    get_script_path,
    get_audit_path,
    get_time_script_path,
    get_time_audit_path,
    get_weather_script_path,
    get_weather_audit_path,
)
from src.ai_radio.api.schemas import (
    ContentItem,
    ContentType,
    DJ,
    ReviewItem,
    ReviewStatus,
    SongInfo,
    AuditResult,
)
from src.ai_radio.api.content import ContentAPI
from src.ai_radio.api.audit import AuditAPI

logger = logging.getLogger(__name__)


class ReviewAPI:
    """API for managing the human review queue.
    
    Provides methods to list pending reviews, approve/reject scripts,
    and queue items for regeneration.
    
    Example:
        api = ReviewAPI()
        
        # Get pending reviews
        pending = api.list_pending_reviews()
        
        # Approve a script
        api.approve(pending[0])
        
        # Reject and queue for regeneration
        api.reject(pending[1], reason="Wrong character voice", queue_regen=True)
    """
    
    def __init__(
        self,
        data_dir: Optional[Path] = None,
        generated_dir: Optional[Path] = None,
        test_mode: bool = False,
    ):
        """Initialize the Review API.
        
        Args:
            data_dir: Override for data directory
            generated_dir: Override for generated content directory
            test_mode: If True, use fake auditor for any re-audits
        """
        self.data_dir = data_dir or DATA_DIR
        self.generated_dir = generated_dir or GENERATED_DIR
        self.test_mode = test_mode
        self._content_api = None
        self._audit_api = None
    
    @property
    def content_api(self) -> ContentAPI:
        """Get or create the content API."""
        if self._content_api is None:
            self._content_api = ContentAPI(
                data_dir=self.data_dir,
                generated_dir=self.generated_dir,
            )
        return self._content_api
    
    @property
    def audit_api(self) -> AuditAPI:
        """Get or create the audit API."""
        if self._audit_api is None:
            self._audit_api = AuditAPI(
                data_dir=self.data_dir,
                test_mode=self.test_mode,
            )
        return self._audit_api
    
    def list_pending_reviews(
        self,
        dj: Optional[DJ] = None,
        content_type: Optional[ContentType] = None,
    ) -> List[ReviewItem]:
        """List items pending human review.
        
        Items pending review are those that have failed audit
        and have not been manually approved or rejected.
        
        Args:
            dj: Filter by DJ (None for all)
            content_type: Filter by content type (None for all)
            
        Returns:
            List of ReviewItem objects
        """
        # Get all failed audit results
        failed_audits = self.audit_api.list_audit_results(dj=dj, passed=False)
        
        # Convert to review items
        items = []
        for audit in failed_audits:
            # Apply content type filter
            if content_type is not None and audit.content_type != content_type:
                continue
            
            # Load the associated content
            content = self._get_content_for_audit(audit)
            if content is None:
                continue
            
            # Check if there's a review status file
            review_status = self._load_review_status(content)
            
            # Only include pending items
            if review_status is None or review_status.get("status") == "pending":
                item = ReviewItem(
                    content=content,
                    audit_result=audit,
                    status=ReviewStatus.PENDING,
                    regeneration_count=review_status.get("regeneration_count", 0) if review_status else 0,
                )
                items.append(item)
        
        return items
    
    def list_all_reviews(
        self,
        dj: Optional[DJ] = None,
        status: Optional[ReviewStatus] = None,
    ) -> List[ReviewItem]:
        """List all items in the review system.
        
        Args:
            dj: Filter by DJ (None for all)
            status: Filter by review status (None for all)
            
        Returns:
            List of ReviewItem objects
        """
        items = []
        
        # Get all audit results (passed and failed)
        all_audits = self.audit_api.list_audit_results(dj=dj)
        
        for audit in all_audits:
            content = self._get_content_for_audit(audit)
            if content is None:
                continue
            
            review_status_data = self._load_review_status(content)
            
            # Determine status
            if review_status_data:
                current_status = ReviewStatus(review_status_data.get("status", "pending"))
            elif audit.passed:
                current_status = ReviewStatus.APPROVED  # Auto-approved
            else:
                current_status = ReviewStatus.PENDING
            
            # Apply status filter
            if status is not None and current_status != status:
                continue
            
            item = ReviewItem(
                content=content,
                audit_result=audit,
                status=current_status,
                reviewer_notes=review_status_data.get("notes", "") if review_status_data else "",
                reviewed_at=datetime.fromisoformat(review_status_data["reviewed_at"]) if review_status_data and "reviewed_at" in review_status_data else None,
                regeneration_count=review_status_data.get("regeneration_count", 0) if review_status_data else 0,
            )
            items.append(item)
        
        return items
    
    def approve(
        self,
        item: ReviewItem,
        notes: str = "",
    ) -> ReviewItem:
        """Approve a script, marking it as ready for use.
        
        Args:
            item: ReviewItem to approve
            notes: Optional reviewer notes
            
        Returns:
            Updated ReviewItem
        """
        # Update the review status
        status_data = {
            "status": "approved",
            "notes": notes,
            "reviewed_at": datetime.now().isoformat(),
            "regeneration_count": item.regeneration_count,
        }
        self._save_review_status(item.content, status_data)
        
        # Update the item
        item.status = ReviewStatus.APPROVED
        item.reviewer_notes = notes
        item.reviewed_at = datetime.now()
        
        logger.info(f"Approved: {item.content.display_name}")
        return item
    
    def reject(
        self,
        item: ReviewItem,
        reason: str = "",
        queue_regen: bool = True,
    ) -> ReviewItem:
        """Reject a script, optionally queuing for regeneration.
        
        Args:
            item: ReviewItem to reject
            reason: Reason for rejection
            queue_regen: If True, add to regeneration queue
            
        Returns:
            Updated ReviewItem
        """
        new_status = ReviewStatus.REGENERATING if queue_regen else ReviewStatus.REJECTED
        
        # Update the review status
        status_data = {
            "status": new_status.value,
            "notes": reason,
            "reviewed_at": datetime.now().isoformat(),
            "regeneration_count": item.regeneration_count + (1 if queue_regen else 0),
        }
        self._save_review_status(item.content, status_data)
        
        # Update the item
        item.status = new_status
        item.reviewer_notes = reason
        item.reviewed_at = datetime.now()
        
        if queue_regen:
            item.regeneration_count += 1
        
        logger.info(f"Rejected{' (queued for regen)' if queue_regen else ''}: {item.content.display_name}")
        return item
    
    def get_regeneration_queue(
        self,
        dj: Optional[DJ] = None,
    ) -> List[ReviewItem]:
        """Get items queued for regeneration.
        
        Args:
            dj: Filter by DJ (None for all)
            
        Returns:
            List of ReviewItem objects marked for regeneration
        """
        return self.list_all_reviews(dj=dj, status=ReviewStatus.REGENERATING)
    
    def mark_regenerated(
        self,
        item: ReviewItem,
    ) -> ReviewItem:
        """Mark an item as regenerated (moves back to pending for re-audit).
        
        Args:
            item: ReviewItem that was regenerated
            
        Returns:
            Updated ReviewItem
        """
        # Update the review status
        status_data = {
            "status": "pending",
            "notes": f"Regenerated (attempt {item.regeneration_count})",
            "reviewed_at": datetime.now().isoformat(),
            "regeneration_count": item.regeneration_count,
        }
        self._save_review_status(item.content, status_data)
        
        item.status = ReviewStatus.PENDING
        
        logger.info(f"Marked as regenerated: {item.content.display_name}")
        return item
    
    def get_review_stats(self, dj: Optional[DJ] = None) -> dict:
        """Get statistics about the review queue.
        
        Args:
            dj: Filter by DJ (None for all)
            
        Returns:
            Dictionary with review statistics
        """
        all_items = self.list_all_reviews(dj=dj)
        
        stats = {
            "total": len(all_items),
            "pending": sum(1 for i in all_items if i.status == ReviewStatus.PENDING),
            "approved": sum(1 for i in all_items if i.status == ReviewStatus.APPROVED),
            "rejected": sum(1 for i in all_items if i.status == ReviewStatus.REJECTED),
            "regenerating": sum(1 for i in all_items if i.status == ReviewStatus.REGENERATING),
        }
        
        # Add by content type
        stats["by_content_type"] = {}
        for ct in ContentType:
            ct_items = [i for i in all_items if i.content.content_type == ct]
            stats["by_content_type"][ct.value] = {
                "total": len(ct_items),
                "pending": sum(1 for i in ct_items if i.status == ReviewStatus.PENDING),
            }
        
        return stats
    
    def _get_content_for_audit(self, audit: AuditResult) -> Optional[ContentItem]:
        """Get the content item associated with an audit result."""
        # Parse the script_id to extract content info
        # Format: {song_id}_{dj}_intro or {hour}-{minute}_{dj}_time etc.
        parts = audit.script_id.rsplit('_', 2)
        if len(parts) < 2:
            return None
        
        dj = audit.dj
        content_type = audit.content_type
        
        try:
            if content_type in [ContentType.INTRO, ContentType.OUTRO]:
                # Load from catalog by looking at script paths
                scripts = self.content_api.list_scripts(dj=dj, content_type=content_type)
                # Match by checking if script_id starts with the song id
                song_id_prefix = parts[0]
                for script in scripts:
                    if script.song and str(script.song.id) == song_id_prefix:
                        return script
            elif content_type == ContentType.TIME:
                # Parse time from script_id (format: HH-MM_dj_time)
                time_part = parts[0]  # e.g., "08-30"
                hour, minute = map(int, time_part.split('-'))
                return self.content_api.get_script(
                    content_type=content_type,
                    dj=dj,
                    hour=hour,
                    minute=minute,
                )
            elif content_type == ContentType.WEATHER:
                # Parse weather from script_id (format: HH-00_dj_weather)
                time_part = parts[0]  # e.g., "12-00"
                hour = int(time_part.split('-')[0])
                return self.content_api.get_script(
                    content_type=content_type,
                    dj=dj,
                    hour=hour,
                )
        except Exception as e:
            logger.warning(f"Error getting content for audit {audit.script_id}: {e}")
        
        return None
    
    def _get_review_status_path(self, content: ContentItem) -> Path:
        """Get the path to the review status file for a content item."""
        if content.script_path:
            return content.script_path.parent / "review_status.json"
        return self.data_dir / "review" / f"{content.display_name}.json"
    
    def _load_review_status(self, content: ContentItem) -> Optional[dict]:
        """Load review status for a content item."""
        status_path = self._get_review_status_path(content)
        if status_path.exists():
            try:
                with open(status_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return None
    
    def _save_review_status(self, content: ContentItem, status: dict):
        """Save review status for a content item."""
        status_path = self._get_review_status_path(content)
        status_path.parent.mkdir(parents=True, exist_ok=True)
        with open(status_path, 'w', encoding='utf-8') as f:
            json.dump(status, f, indent=2, ensure_ascii=False)
