"""Backend API layer for AI Radio.

This package provides a clean Python API for GUI and automation tools
to interact with the AI Radio generation pipeline without CLI dependencies.

Example usage:
    from src.ai_radio.api import ContentAPI, GenerationAPI, AuditAPI, ReviewAPI
    
    # List available content
    content_api = ContentAPI()
    scripts = content_api.list_scripts(dj="julie", content_type="intros")
    
    # Trigger generation
    gen_api = GenerationAPI()
    result = gen_api.generate_intro(song_id="1", artist="Artist", title="Song", dj="julie")
    
    # Check audit results
    audit_api = AuditAPI()
    results = audit_api.list_audit_results(dj="julie", status="passed")
    
    # Manage review queue
    review_api = ReviewAPI()
    pending = review_api.list_pending_reviews()
"""

from src.ai_radio.api.schemas import (
    ContentItem,
    GenerationResult,
    AuditResult,
    ReviewItem,
    ContentType,
    ReviewStatus,
    DJ,
)
from src.ai_radio.api.content import ContentAPI
from src.ai_radio.api.generation import GenerationAPI
from src.ai_radio.api.audit import AuditAPI
from src.ai_radio.api.review import ReviewAPI

__all__ = [
    # Schemas
    "ContentItem",
    "GenerationResult",
    "AuditResult",
    "ReviewItem",
    "ContentType",
    "ReviewStatus",
    "DJ",
    # APIs
    "ContentAPI",
    "GenerationAPI",
    "AuditAPI",
    "ReviewAPI",
]
