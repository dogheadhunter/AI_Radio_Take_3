"""Content discovery and listing API.

This module provides functions to discover and list generated content,
including scripts and audio files for all content types.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from src.ai_radio.config import DATA_DIR, GENERATED_DIR, CATALOG_FILE, WEATHER_TIMES
from src.ai_radio.core.paths import (
    get_script_path,
    get_audio_path,
    get_audit_path,
    get_time_script_path,
    get_time_audio_path,
    get_time_audit_path,
    get_weather_script_path,
    get_weather_audio_path,
    get_weather_audit_path,
)
from src.ai_radio.api.schemas import (
    ContentItem,
    ContentType,
    ContentFilter,
    DJ,
    SongInfo,
    AuditStatus,
    PipelineStatus,
)


class ContentAPI:
    """API for discovering and listing generated content.
    
    Provides methods to list scripts, audio files, and query
    content by various filters without any CLI or UI dependencies.
    
    Example:
        api = ContentAPI()
        scripts = api.list_scripts(dj=DJ.JULIE, content_type=ContentType.INTRO)
        print(f"Found {len(scripts)} intro scripts for Julie")
    """
    
    def __init__(self, data_dir: Optional[Path] = None, generated_dir: Optional[Path] = None):
        """Initialize the Content API.
        
        Args:
            data_dir: Override for data directory (default: config.DATA_DIR)
            generated_dir: Override for generated content directory
        """
        self.data_dir = data_dir or DATA_DIR
        self.generated_dir = generated_dir or GENERATED_DIR
        self._catalog_cache: Optional[List[SongInfo]] = None
    
    def load_catalog(self, force_reload: bool = False) -> List[SongInfo]:
        """Load the song catalog.
        
        Args:
            force_reload: If True, reload from disk even if cached
            
        Returns:
            List of SongInfo objects from catalog
        """
        if self._catalog_cache is not None and not force_reload:
            return self._catalog_cache
        
        catalog_path = self.data_dir / "catalog.json"
        if not catalog_path.exists():
            return []
        
        with open(catalog_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        songs = [
            SongInfo(id=str(s['id']), artist=s['artist'], title=s['title'])
            for s in data.get('songs', [])
        ]
        self._catalog_cache = songs
        return songs
    
    def list_scripts(
        self,
        dj: Optional[DJ] = None,
        content_type: Optional[ContentType] = None,
        include_text: bool = False,
    ) -> List[ContentItem]:
        """List all generated scripts.
        
        Args:
            dj: Filter by DJ (None for all DJs)
            content_type: Filter by content type (None for all types)
            include_text: If True, load script text into ContentItem
            
        Returns:
            List of ContentItem objects for matching scripts
        """
        items = []
        djs = [dj] if dj else [DJ.JULIE, DJ.MR_NEW_VEGAS]
        types = [content_type] if content_type else list(ContentType)
        
        for d in djs:
            for ct in types:
                if ct == ContentType.INTRO or ct == ContentType.OUTRO:
                    items.extend(self._list_song_scripts(d, ct, include_text))
                elif ct == ContentType.TIME:
                    items.extend(self._list_time_scripts(d, include_text))
                elif ct == ContentType.WEATHER:
                    items.extend(self._list_weather_scripts(d, include_text))
        
        return items
    
    def _list_song_scripts(
        self, dj: DJ, content_type: ContentType, include_text: bool
    ) -> List[ContentItem]:
        """List song-based scripts (intros/outros)."""
        items = []
        songs = self.load_catalog()
        path_type = "intros" if content_type == ContentType.INTRO else "outros"
        
        for song in songs:
            script_path = get_script_path(song.to_dict(), dj.value, content_type=path_type)
            if script_path.exists():
                audio_path = get_audio_path(song.to_dict(), dj.value, content_type=path_type)
                
                item = ContentItem(
                    content_type=content_type,
                    dj=dj,
                    script_path=script_path,
                    audio_path=audio_path if audio_path.exists() else None,
                    song=song,
                )
                
                if include_text:
                    item.script_text = script_path.read_text(encoding='utf-8')
                
                # Get creation time from file
                item.created_at = datetime.fromtimestamp(script_path.stat().st_mtime)
                items.append(item)
        
        return items
    
    def _list_time_scripts(self, dj: DJ, include_text: bool) -> List[ContentItem]:
        """List time announcement scripts."""
        items = []
        # All 48 time slots
        time_slots = [(h, m) for h in range(24) for m in [0, 30]]
        
        for hour, minute in time_slots:
            script_path = get_time_script_path(hour, minute, dj.value)
            if script_path.exists():
                audio_path = get_time_audio_path(hour, minute, dj.value)
                
                item = ContentItem(
                    content_type=ContentType.TIME,
                    dj=dj,
                    script_path=script_path,
                    audio_path=audio_path if audio_path.exists() else None,
                    hour=hour,
                    minute=minute,
                )
                
                if include_text:
                    item.script_text = script_path.read_text(encoding='utf-8')
                
                item.created_at = datetime.fromtimestamp(script_path.stat().st_mtime)
                items.append(item)
        
        return items
    
    def _list_weather_scripts(self, dj: DJ, include_text: bool) -> List[ContentItem]:
        """List weather announcement scripts."""
        items = []
        
        for hour in WEATHER_TIMES:
            script_path = get_weather_script_path(hour, dj.value)
            if script_path.exists():
                audio_path = get_weather_audio_path(hour, dj.value)
                
                item = ContentItem(
                    content_type=ContentType.WEATHER,
                    dj=dj,
                    script_path=script_path,
                    audio_path=audio_path if audio_path.exists() else None,
                    weather_hour=hour,
                )
                
                if include_text:
                    item.script_text = script_path.read_text(encoding='utf-8')
                
                item.created_at = datetime.fromtimestamp(script_path.stat().st_mtime)
                items.append(item)
        
        return items
    
    def get_script(
        self,
        content_type: ContentType,
        dj: DJ,
        song: Optional[SongInfo] = None,
        hour: Optional[int] = None,
        minute: Optional[int] = None,
    ) -> Optional[ContentItem]:
        """Get a specific script by its identifiers.
        
        Args:
            content_type: Type of content
            dj: DJ personality
            song: Song info (required for INTRO/OUTRO)
            hour: Hour (required for TIME/WEATHER)
            minute: Minute (required for TIME, optional for WEATHER)
            
        Returns:
            ContentItem if found, None otherwise
        """
        script_path: Optional[Path] = None
        audio_path: Optional[Path] = None
        
        if content_type in [ContentType.INTRO, ContentType.OUTRO]:
            if song is None:
                return None
            path_type = "intros" if content_type == ContentType.INTRO else "outros"
            script_path = get_script_path(song.to_dict(), dj.value, content_type=path_type)
            audio_path = get_audio_path(song.to_dict(), dj.value, content_type=path_type)
            
        elif content_type == ContentType.TIME:
            if hour is None or minute is None:
                return None
            script_path = get_time_script_path(hour, minute, dj.value)
            audio_path = get_time_audio_path(hour, minute, dj.value)
            
        elif content_type == ContentType.WEATHER:
            if hour is None:
                return None
            script_path = get_weather_script_path(hour, dj.value)
            audio_path = get_weather_audio_path(hour, dj.value)
        
        if script_path is None or not script_path.exists():
            return None
        
        item = ContentItem(
            content_type=content_type,
            dj=dj,
            script_path=script_path,
            audio_path=audio_path if audio_path and audio_path.exists() else None,
            script_text=script_path.read_text(encoding='utf-8'),
            song=song,
            hour=hour,
            minute=minute,
            weather_hour=hour if content_type == ContentType.WEATHER else None,
        )
        item.created_at = datetime.fromtimestamp(script_path.stat().st_mtime)
        
        return item
    
    def get_pipeline_status(self) -> PipelineStatus:
        """Get current pipeline status from checkpoint.
        
        Returns:
            PipelineStatus with current progress information
        """
        checkpoint_path = self.data_dir / "pipeline_state.json"
        
        if not checkpoint_path.exists():
            return PipelineStatus()
        
        with open(checkpoint_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        stages = data.get("stages", {})
        gen_stage = stages.get("generate", {})
        audit_stage = stages.get("audit", {})
        audio_stage = stages.get("audio", {})
        
        return PipelineStatus(
            generate_completed=gen_stage.get("status") == "completed",
            audit_completed=audit_stage.get("status") == "completed",
            audio_completed=audio_stage.get("status") == "completed",
            scripts_generated=gen_stage.get("scripts_generated", 0),
            scripts_audited=audit_stage.get("scripts_audited", 0),
            scripts_passed=audit_stage.get("passed", 0),
            scripts_failed=audit_stage.get("failed", 0),
            audio_files_generated=audio_stage.get("audio_files_generated", 0),
            run_id=data.get("run_id"),
            last_updated=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else None,
        )
    
    def count_content(
        self,
        dj: Optional[DJ] = None,
        content_type: Optional[ContentType] = None,
    ) -> dict:
        """Count scripts and audio files.
        
        Args:
            dj: Filter by DJ (None for all)
            content_type: Filter by content type (None for all)
            
        Returns:
            Dictionary with counts: {scripts, audio_files, songs_in_catalog}
        """
        scripts = self.list_scripts(dj=dj, content_type=content_type)
        
        return {
            "scripts": len(scripts),
            "audio_files": sum(1 for s in scripts if s.has_audio),
            "songs_in_catalog": len(self.load_catalog()),
        }
