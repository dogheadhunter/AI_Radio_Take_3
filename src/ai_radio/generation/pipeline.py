"""Generation pipeline that orchestrates LLM -> TTS."""
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Callable, Optional, List, Dict, Any
from src.ai_radio.generation.llm_client import LLMClient, generate_text
from src.ai_radio.generation.tts_client import TTSClient, generate_audio
from src.ai_radio.generation.prompts import build_song_intro_prompt, build_time_announcement_prompt, build_weather_prompt, build_song_outro_prompt, DJ
from src.ai_radio.generation.lyrics_parser import match_lyrics_to_catalog, extract_lyrics_context
from src.ai_radio.utils.errors import GenerationError
from src.ai_radio.config import VOICE_REFERENCES_DIR


@dataclass
class GenerationResult:
    song_id: str
    dj: str
    text: Optional[str]
    audio_path: Optional[Path]
    success: bool
    error: Optional[str] = None
    skipped: bool = False


@dataclass
class BatchProgress:
    total: int
    completed: int
    failed: int
    current_song: str

    @property
    def percent(self) -> float:
        return (self.completed / self.total) * 100 if self.total > 0 else 0.0


class GenerationPipeline:
    def __init__(self, output_dir: Optional[Path] = None, prompt_version: str = "v1", lyrics_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path("data/generated")
        self._llm_loaded = False
        self._tts_loaded = False
        self._llm = LLMClient()
        self._tts = TTSClient()
        # Prompt version: 'v1' (legacy) or 'v2' (improved templates)
        self.prompt_version = prompt_version

        # Lyrics support: optional directory with parsed lyric files
        self._lyrics_map = {}
        if lyrics_dir is not None and lyrics_dir.exists():
            # Attempt to load catalog to match lyrics against
            try:
                import json
                catalog_path = Path("data/catalog.json")
                if catalog_path.exists():
                    catalog = json.loads(catalog_path.read_text(encoding='utf-8'))
                else:
                    catalog = []
                self._lyrics_map = match_lyrics_to_catalog(lyrics_dir, catalog)
            except Exception:
                # Fail gracefully - leave empty mapping
                self._lyrics_map = {}

    def _make_song_folder(self, song_id: str, artist: str, title: str, dj: str) -> Path:
        """Create a human-readable folder for this song's generated content, organized by DJ."""
        # Sanitize artist and title for filesystem
        safe_artist = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in artist)
        safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in title)
        safe_artist = safe_artist.strip().replace(' ', '_')
        safe_title = safe_title.strip().replace(' ', '_')
        
        folder_name = f"{safe_artist}-{safe_title}"
        folder_path = self.output_dir / "intros" / dj / folder_name
        folder_path.mkdir(parents=True, exist_ok=True)
        return folder_path

    def generate_song_intro(self, song_id: str, artist: str, title: str, dj: str, text_only: bool = False, audio_only: bool = False, lyrics_context: str = None, audit_feedback: str = None, version: int = None) -> GenerationResult:
        """Generate song intro with versioning and dual audio support.
        
        Args:
            version: If None, auto-detect next version number. If specified, use that version.
                    For regeneration, pass the next version number to preserve previous versions.
        """
        try:
            # Create song folder
            song_folder = self._make_song_folder(song_id, artist, title, dj)
            
            # Auto-detect version if not specified
            if version is None:
                version = self._get_next_version(song_folder, dj, "intros")
            
            text_path = song_folder / f"{dj}_{version}.txt"
            audio_path_full = song_folder / f"{dj}_{version}_full.wav"
            audio_path_30sec = song_folder / f"{dj}_{version}_30sec.wav"
            # Legacy single audio path (for backwards compatibility in result)
            audio_path = song_folder / f"{dj}_{version}.wav"
            
            text = None
            
            # Generate text (unless audio_only mode)
            if not audio_only:
                self._llm_loaded = True
                # Use v2 prompts if configured
                if getattr(self, 'prompt_version', 'v1') == 'v2':
                    from src.ai_radio.generation.prompts_v2 import build_song_intro_prompt_v2, FORBIDDEN_WORDS
                    p = build_song_intro_prompt_v2(DJ(dj), artist=artist, title=title, lyrics_context=lyrics_context, audit_feedback=audit_feedback)
                    prompt = p['system'] + "\n\n" + p['user']
                    # Pass banned phrases to enable repeat_penalty (nuclear option for semantic override)
                    text = generate_text(self._llm, prompt, banned_phrases=FORBIDDEN_WORDS)
                else:
                    prompt = build_song_intro_prompt(DJ(dj), artist=artist, title=title)
                    text = generate_text(self._llm, prompt)
                self._llm_loaded = False

                # Save text script
                text_path.write_text(text, encoding='utf-8')
            
            # Generate audio (unless text_only mode)
            if not text_only:
                # Load text if in audio_only mode
                if audio_only:
                    if text_path.exists():
                        text = text_path.read_text(encoding='utf-8')
                    else:
                        # Try previous version's text file if audio_only and new version
                        prev_text_path = song_folder / f"{dj}_{version-1}.txt" if version > 0 else None
                        if prev_text_path and prev_text_path.exists():
                            text = prev_text_path.read_text(encoding='utf-8')
                        else:
                            # Check legacy doubled path structure (intros/intros/dj/...)
                            safe_artist = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in artist).strip().replace(' ', '_')
                            safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in title).strip().replace(' ', '_')
                            legacy_text_path = self.output_dir / "intros" / "intros" / dj / f"{safe_artist}-{safe_title}" / f"{dj}_0.txt"
                            if legacy_text_path.exists():
                                text = legacy_text_path.read_text(encoding='utf-8')
                            else:
                                raise FileNotFoundError(f"Text file not found for audio generation: {text_path}")
                
                # Generate DUAL audio: full voice sample and 30-second sample
                dj_folder = "Julie" if dj == "julie" else "Mister_New_Vegas"
                
                # Full voice reference
                voice_ref_full = VOICE_REFERENCES_DIR / dj_folder / f"{dj}.wav"
                if voice_ref_full.exists():
                    generate_audio(self._tts, text=text, output_path=audio_path_full, voice_reference=voice_ref_full)
                
                # 30-second voice reference
                voice_ref_30sec = VOICE_REFERENCES_DIR / dj_folder / f"{dj}_30sec.wav"
                if voice_ref_30sec.exists():
                    generate_audio(self._tts, text=text, output_path=audio_path_30sec, voice_reference=voice_ref_30sec)
                elif voice_ref_full.exists():
                    # Fallback: if no 30sec exists, just generate with full ref as legacy single file
                    generate_audio(self._tts, text=text, output_path=audio_path, voice_reference=voice_ref_full)

            return GenerationResult(song_id=song_id, dj=dj, text=text, audio_path=audio_path_full if not text_only else None, success=True)
        except Exception as exc:
            return GenerationResult(song_id=song_id, dj=dj, text=None, audio_path=None, success=False, error=str(exc))
    
    def _get_next_version(self, folder: Path, dj: str, content_type: str) -> int:
        """Get next version number by scanning existing files in folder."""
        import re
        if not folder.exists():
            return 0
        
        versions = set()
        
        if content_type == "outros":
            # Outros: dj_outro.txt (v0), dj_outro_1.txt (v1), etc.
            for f in folder.glob(f"{dj}_outro*.txt"):
                if f.stem == f"{dj}_outro":
                    versions.add(0)
                else:
                    match = re.search(r'_outro_(\d+)', f.stem)
                    if match:
                        versions.add(int(match.group(1)))
            for f in folder.glob(f"{dj}_outro*.wav"):
                if f.stem == f"{dj}_outro":
                    versions.add(0)
                else:
                    match = re.search(r'_outro_(\d+)', f.stem)
                    if match:
                        versions.add(int(match.group(1)))
        else:
            # Intros and others: dj_0.txt, dj_1.txt, dj_0_full.wav, dj_0_30sec.wav, etc.
            for f in folder.glob(f"{dj}_*.txt"):
                match = re.search(rf'{dj}_(\d+)\.txt$', f.name)
                if match:
                    versions.add(int(match.group(1)))
            for f in folder.glob(f"{dj}_*.wav"):
                # Match both legacy (dj_0.wav) and new (dj_0_full.wav, dj_0_30sec.wav)
                match = re.search(rf'{dj}_(\d+)(?:_(?:full|30sec))?\.wav$', f.name)
                if match:
                    versions.add(int(match.group(1)))
        
        return max(versions) + 1 if versions else 0

    def generate_batch_intros(
        self,
        songs: List[Dict[str, Any]],
        dj: str = "julie",
        resume: bool = False,
        progress_callback: Optional[Callable[[BatchProgress], None]] = None,
        two_phase: bool = False,
    ) -> Iterator[GenerationResult]:
        total = len(songs)
        completed = 0
        failed = 0

        # Two-phase mode: generate all scripts first, then all audio
        if two_phase:
            # Phase 1: Generate all text scripts
            for s in songs:
                current_song = s.get("title") or s.get("id")
                safe_artist = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in s.get("artist", "Unknown"))
                safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in s.get("title", "Unknown"))
                safe_artist = safe_artist.strip().replace(' ', '_')
                safe_title = safe_title.strip().replace(' ', '_')
                folder_name = f"{safe_artist}-{safe_title}"
                text_path = self.output_dir / "intros" / dj / folder_name / f"{dj}_0.txt"
                
                if resume and text_path.exists():
                    completed += 1
                    if progress_callback:
                        progress_callback(BatchProgress(total=total, completed=completed, failed=failed, current_song=current_song))
                    continue
                
                # Include lyrics context when available
                lyrics_ctx = None
                ldata = self._lyrics_map.get(str(s.get("id")))
                if ldata:
                    try:
                        lyrics_ctx = ldata.lyrics if not ldata.is_instrumental else "[Instrumental - no lyrics]"
                    except Exception:
                        lyrics_ctx = None

                result = self.generate_song_intro(s["id"], artist=s.get("artist"), title=s.get("title"), dj=dj, text_only=True, lyrics_context=lyrics_ctx)
                if result.success:
                    completed += 1
                else:
                    failed += 1
                
                if progress_callback:
                    progress_callback(BatchProgress(total=total, completed=completed, failed=failed, current_song=current_song))
            
            # Reset counters for Phase 2
            completed = 0
            failed = 0
            
            # Phase 2: Generate all audio
            for s in songs:
                current_song = s.get("title") or s.get("id")
                safe_artist = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in s.get("artist", "Unknown"))
                safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in s.get("title", "Unknown"))
                safe_artist = safe_artist.strip().replace(' ', '_')
                safe_title = safe_title.strip().replace(' ', '_')
                folder_name = f"{safe_artist}-{safe_title}"
                audio_path = self.output_dir / "intros" / dj / folder_name / f"{dj}_0.wav"
                
                if resume and audio_path.exists():
                    completed += 1
                    res = GenerationResult(song_id=s["id"], dj=dj, text=None, audio_path=audio_path, success=True, skipped=True)
                    if progress_callback:
                        progress_callback(BatchProgress(total=total, completed=completed, failed=failed, current_song=current_song))
                    yield res
                    continue
                
                # Include lyrics context when available
                lyrics_ctx = None
                ldata = self._lyrics_map.get(str(s.get("id")))
                if ldata:
                    try:
                        lyrics_ctx = ldata.lyrics if not ldata.is_instrumental else "[Instrumental - no lyrics]"
                    except Exception:
                        lyrics_ctx = None

                result = self.generate_song_intro(s["id"], artist=s.get("artist"), title=s.get("title"), dj=dj, audio_only=True, lyrics_context=lyrics_ctx)
                if result.success:
                    completed += 1
                else:
                    failed += 1
                
                if progress_callback:
                    progress_callback(BatchProgress(total=total, completed=completed, failed=failed, current_song=current_song))
                
                yield result
        else:
            # Original single-phase mode
            for s in songs:
                current_song = s.get("title") or s.get("id")
                if resume:
                    # Check for existing audio in DJ-specific song folder
                    safe_artist = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in s.get("artist", "Unknown"))
                    safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in s.get("title", "Unknown"))
                    safe_artist = safe_artist.strip().replace(' ', '_')
                    safe_title = safe_title.strip().replace(' ', '_')
                    folder_name = f"{safe_artist}-{safe_title}"
                    existing = self.output_dir / "intros" / dj / folder_name / f"{dj}_0.wav"
                    
                    if existing.exists():
                        completed += 1
                        res = GenerationResult(song_id=s["id"], dj=dj, text=None, audio_path=existing, success=True, skipped=True)
                        if progress_callback:
                            progress_callback(BatchProgress(total=total, completed=completed, failed=failed, current_song=current_song))
                        yield res
                        continue

                # Include lyrics context when available
                lyrics_ctx = None
                ldata = self._lyrics_map.get(str(s.get("id")))
                if ldata:
                    try:
                        lyrics_ctx = ldata.lyrics if not ldata.is_instrumental else "[Instrumental - no lyrics]"
                    except Exception:
                        lyrics_ctx = None

                result = self.generate_song_intro(s["id"], artist=s.get("artist"), title=s.get("title"), dj=dj, lyrics_context=lyrics_ctx)
                if result.success:
                    completed += 1
                else:
                    failed += 1

                if progress_callback:
                    progress_callback(BatchProgress(total=total, completed=completed, failed=failed, current_song=current_song))

                yield result

    def generate_time_announcement(self, hour: int, minute: int, dj: str, text_only: bool = False, audio_only: bool = False) -> GenerationResult:
        """Generate a single time announcement for given hour/minute and DJ."""
        try:
            time_str = f"{hour:02d}-{minute:02d}"
            folder = self.output_dir / "time" / dj / time_str
            folder.mkdir(parents=True, exist_ok=True)
            text_path = folder / f"{dj}_0.txt"
            audio_path = folder / f"{dj}_0.wav"
            
            text = None
            
            # Generate text (unless audio_only mode)
            if not audio_only:
                # Build prompt (v2 if configured)
                if getattr(self, 'prompt_version', 'v1') == 'v2':
                    from src.ai_radio.generation.prompts_v2 import build_time_prompt_v2
                    p = build_time_prompt_v2(DJ(dj), hour=hour, minute=minute)
                    prompt = p['system'] + "\n\n" + p['user']
                else:
                    prompt = build_time_announcement_prompt(hour=hour, minute=minute, dj=DJ(dj))

                # Generate text
                self._llm_loaded = True
                text = generate_text(self._llm, prompt)
                self._llm_loaded = False

                # Save script
                text_path.write_text(text, encoding='utf-8')

            # Generate audio (unless text_only mode)
            if not text_only:
                # Load text if in audio_only mode
                if audio_only:
                    if text_path.exists():
                        text = text_path.read_text(encoding='utf-8')
                    else:
                        raise FileNotFoundError(f"Text file not found for audio generation: {text_path}")
                
                dj_folder = "Julie" if dj == "julie" else "Mister_New_Vegas"
                voice_ref = VOICE_REFERENCES_DIR / dj_folder / f"{dj}.wav"
                if not voice_ref.exists():
                    voice_ref = None

                generate_audio(self._tts, text=text, output_path=audio_path, voice_reference=voice_ref)

            return GenerationResult(song_id=f"time_{hour:02d}{minute:02d}", dj=dj, text=text, audio_path=audio_path if not text_only else None, success=True)
        except Exception as exc:
            return GenerationResult(song_id=f"time_{hour:02d}{minute:02d}", dj=dj, text=None, audio_path=None, success=False, error=str(exc))

    def generate_weather_announcement(self, hour: int, minute: int, dj: str, weather_data: Optional[Dict[str, Any]] = None, text_only: bool = False, audio_only: bool = False) -> GenerationResult:
        """Generate a single weather announcement and save weather metadata if provided."""
        try:
            time_str = f"{hour:02d}-{minute:02d}"
            folder = self.output_dir / "weather" / dj / time_str
            folder.mkdir(parents=True, exist_ok=True)
            text_path = folder / f"{dj}_0.txt"
            audio_path = folder / f"{dj}_0.wav"
            
            text = None
            
            # Generate text (unless audio_only mode)
            if not audio_only:
                # Handle both dict and WeatherData dataclass
                if weather_data is None:
                    summary = ""
                elif hasattr(weather_data, 'temperature') and hasattr(weather_data, 'conditions'):
                    # WeatherData dataclass - format temperature as integer to avoid long decimals
                    temp_str = f"{int(round(weather_data.temperature))} degrees Fahrenheit" if weather_data.temperature else "unknown temperature"
                    cond_str = weather_data.conditions or "unknown conditions"
                    summary = f"{temp_str}, {cond_str}"
                else:
                    # Dict format
                    summary = weather_data.get('summary', '')
                # Build prompt (v2 if configured)
                if getattr(self, 'prompt_version', 'v1') == 'v2':
                    from src.ai_radio.generation.prompts_v2 import build_weather_prompt_v2
                    p = build_weather_prompt_v2(DJ(dj), summary, hour=hour)
                    prompt = p['system'] + "\n\n" + p['user']
                else:
                    prompt = build_weather_prompt(DJ(dj), summary, hour=hour)

                self._llm_loaded = True
                text = generate_text(self._llm, prompt)
                self._llm_loaded = False

                # Save script
                text_path.write_text(text, encoding='utf-8')

                # Save metadata
                if weather_data is not None:
                    import json
                    from dataclasses import asdict
                    # Convert WeatherData to dict if it's a dataclass
                    if hasattr(weather_data, '__dataclass_fields__'):
                        weather_dict = asdict(weather_data)
                    else:
                        weather_dict = weather_data
                    (folder / "weather_data.json").write_text(json.dumps(weather_dict, indent=2), encoding='utf-8')

            # Generate audio (unless text_only mode)
            if not text_only:
                # Load text if in audio_only mode
                if audio_only:
                    if text_path.exists():
                        text = text_path.read_text(encoding='utf-8')
                    else:
                        raise FileNotFoundError(f"Text file not found for audio generation: {text_path}")
                
                dj_folder = "Julie" if dj == "julie" else "Mister_New_Vegas"
                voice_ref = VOICE_REFERENCES_DIR / dj_folder / f"{dj}.wav"
                if not voice_ref.exists():
                    voice_ref = None

                generate_audio(self._tts, text=text, output_path=audio_path, voice_reference=voice_ref)

            return GenerationResult(song_id=f"weather_{hour:02d}{minute:02d}", dj=dj, text=text, audio_path=audio_path if not text_only else None, success=True)
        except Exception as exc:
            return GenerationResult(song_id=f"weather_{hour:02d}{minute:02d}", dj=dj, text=None, audio_path=None, success=False, error=str(exc))

    def generate_song_outro(self, song_id: str, artist: str, title: str, dj: str, next_song: str = None, text_only: bool = False, audio_only: bool = False, lyrics_context: str = None, audit_feedback: str = None, version: int = None) -> GenerationResult:
        """Generate a short outro for a song with versioning and dual audio support.
        
        Args:
            version: If None, auto-detect next version number. If specified, use that version.
        """
        try:
            # Create folder similar to intros
            safe_artist = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in artist)
            safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in title)
            safe_artist = safe_artist.strip().replace(' ', '_')
            safe_title = safe_title.strip().replace(' ', '_')
            folder_name = f"{safe_artist}-{safe_title}"
            folder = self.output_dir / "outros" / dj / folder_name
            folder.mkdir(parents=True, exist_ok=True)
            
            # Auto-detect version if not specified
            if version is None:
                version = self._get_next_version(folder, dj, "outros")
            
            # Naming: outro v0 = dj_outro.txt, v1+ = dj_outro_1.txt
            if version == 0:
                text_path = folder / f"{dj}_outro.txt"
                audio_path_full = folder / f"{dj}_outro_full.wav"
                audio_path_30sec = folder / f"{dj}_outro_30sec.wav"
                audio_path = folder / f"{dj}_outro.wav"
            else:
                text_path = folder / f"{dj}_outro_{version}.txt"
                audio_path_full = folder / f"{dj}_outro_{version}_full.wav"
                audio_path_30sec = folder / f"{dj}_outro_{version}_30sec.wav"
                audio_path = folder / f"{dj}_outro_{version}.wav"
            
            text = None
            
            # Generate text (unless audio_only mode)
            if not audio_only:
                # Build prompt (v2 if configured)
                if getattr(self, 'prompt_version', 'v1') == 'v2':
                    from src.ai_radio.generation.prompts_v2 import build_song_outro_prompt_v2
                    p = build_song_outro_prompt_v2(DJ(dj), artist=artist, title=title, next_song=next_song, lyrics_context=lyrics_context, audit_feedback=audit_feedback)
                    prompt = p['system'] + "\n\n" + p['user']
                else:
                    prompt = build_song_outro_prompt(DJ(dj), artist=artist, title=title, next_song=next_song)

                self._llm_loaded = True
                text = generate_text(self._llm, prompt)
                self._llm_loaded = False

                text_path.write_text(text, encoding='utf-8')

            # Generate audio (unless text_only mode)
            if not text_only:
                # Load text if in audio_only mode
                if audio_only:
                    if text_path.exists():
                        text = text_path.read_text(encoding='utf-8')
                    else:
                        # Try previous version's text file
                        if version == 1:
                            prev_text_path = folder / f"{dj}_outro.txt"
                        elif version > 1:
                            prev_text_path = folder / f"{dj}_outro_{version-1}.txt"
                        else:
                            prev_text_path = None
                        
                        if prev_text_path and prev_text_path.exists():
                            text = prev_text_path.read_text(encoding='utf-8')
                        else:
                            # Check legacy doubled path structure (outros/outros/dj/...)
                            safe_artist = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in artist).strip().replace(' ', '_')
                            safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in title).strip().replace(' ', '_')
                            legacy_text_path = self.output_dir / "outros" / "outros" / dj / f"{safe_artist}-{safe_title}" / f"{dj}_outro.txt"
                            if legacy_text_path.exists():
                                text = legacy_text_path.read_text(encoding='utf-8')
                            else:
                                raise FileNotFoundError(f"Text file not found for audio generation: {text_path}")
                
                # Generate DUAL audio: full voice sample and 30-second sample
                dj_folder = "Julie" if dj == "julie" else "Mister_New_Vegas"
                
                # Full voice reference
                voice_ref_full = VOICE_REFERENCES_DIR / dj_folder / f"{dj}.wav"
                if voice_ref_full.exists():
                    generate_audio(self._tts, text=text, output_path=audio_path_full, voice_reference=voice_ref_full)
                
                # 30-second voice reference
                voice_ref_30sec = VOICE_REFERENCES_DIR / dj_folder / f"{dj}_30sec.wav"
                if voice_ref_30sec.exists():
                    generate_audio(self._tts, text=text, output_path=audio_path_30sec, voice_reference=voice_ref_30sec)
                elif voice_ref_full.exists():
                    # Fallback: if no 30sec exists, just generate with full ref as legacy single file
                    generate_audio(self._tts, text=text, output_path=audio_path, voice_reference=voice_ref_full)

            return GenerationResult(song_id=song_id, dj=dj, text=text, audio_path=audio_path_full if not text_only else None, success=True)
        except Exception as exc:
            return GenerationResult(song_id=song_id, dj=dj, text=None, audio_path=None, success=False, error=str(exc))


def generate_song_intro(pipeline: GenerationPipeline, song_id: str, artist: str, title: str, dj: str, lyrics_context: str = None) -> GenerationResult:
    """Module-level helper function that delegates to a pipeline instance."""
    return pipeline.generate_song_intro(song_id=song_id, artist=artist, title=title, dj=dj, lyrics_context=lyrics_context)


def generate_batch_intros(
    pipeline: GenerationPipeline,
    songs: List[Dict[str, Any]],
    dj: str = "julie",
    resume: bool = False,
    progress_callback: Optional[Callable[[BatchProgress], None]] = None,
    two_phase: bool = False,
) -> Iterator[GenerationResult]:
    return pipeline.generate_batch_intros(songs, dj=dj, resume=resume, progress_callback=progress_callback, two_phase=two_phase)


def generate_time_announcement(pipeline: GenerationPipeline, hour: int, minute: int, dj: str) -> GenerationResult:
    return pipeline.generate_time_announcement(hour=hour, minute=minute, dj=dj)


def generate_batch_time_announcements(
    pipeline: GenerationPipeline,
    dj: str = "julie",
    resume: bool = False,
    progress_callback: Optional[Callable[[BatchProgress], None]] = None,
    two_phase: bool = False,
) -> Iterator[GenerationResult]:
    # Build 48 slots (every 30 minutes)
    time_slots = [(h, m) for h in range(24) for m in (0, 30)]
    total = len(time_slots)
    completed = 0
    failed = 0

    # Two-phase mode: generate all scripts first, then all audio
    if two_phase:
        # Phase 1: Generate all text scripts
        for hour, minute in time_slots:
            current_slot = f"{hour:02d}-{minute:02d}"
            text_path = pipeline.output_dir / "time" / dj / current_slot / f"{dj}_0.txt"
            
            if resume and text_path.exists():
                completed += 1
                if progress_callback:
                    progress_callback(BatchProgress(total=total, completed=completed, failed=failed, current_song=current_slot))
                continue
            
            result = pipeline.generate_time_announcement(hour=hour, minute=minute, dj=dj, text_only=True)
            if result.success:
                completed += 1
            else:
                failed += 1
            
            if progress_callback:
                progress_callback(BatchProgress(total=total, completed=completed, failed=failed, current_song=current_slot))
        
        # Reset counters for Phase 2
        completed = 0
        failed = 0
        
        # Phase 2: Generate all audio
        for hour, minute in time_slots:
            current_slot = f"{hour:02d}-{minute:02d}"
            audio_path = pipeline.output_dir / "time" / dj / current_slot / f"{dj}_0.wav"
            
            if resume and audio_path.exists():
                completed += 1
                yield GenerationResult(song_id=f"time_{hour:02d}{minute:02d}", dj=dj, text=None, audio_path=audio_path, success=True, skipped=True)
                if progress_callback:
                    progress_callback(BatchProgress(total=total, completed=completed, failed=failed, current_song=current_slot))
                continue
            
            result = pipeline.generate_time_announcement(hour=hour, minute=minute, dj=dj, audio_only=True)
            if result.success:
                completed += 1
            else:
                failed += 1
            
            if progress_callback:
                progress_callback(BatchProgress(total=total, completed=completed, failed=failed, current_song=current_slot))
            
            yield result
    else:
        # Original single-phase mode
        for hour, minute in time_slots:
            current_slot = f"{hour:02d}-{minute:02d}"
            # Check existing when resuming
            audio_path = pipeline.output_dir / "time" / dj / current_slot / f"{dj}_0.wav"
            if resume and audio_path.exists():
                completed += 1
                # Create a skipped result
                yield GenerationResult(song_id=f"time_{hour:02d}{minute:02d}", dj=dj, text=None, audio_path=audio_path, success=True, skipped=True)
                if progress_callback:
                    progress_callback(BatchProgress(total=total, completed=completed, failed=failed, current_song=current_slot))
                continue

            result = pipeline.generate_time_announcement(hour=hour, minute=minute, dj=dj)
            if result.success:
                completed += 1
            else:
                failed += 1
            if progress_callback:
                progress_callback(BatchProgress(total=total, completed=completed, failed=failed, current_song=current_slot))

            yield result


def generate_weather_announcement(pipeline: GenerationPipeline, hour: int, minute: int, dj: str, weather_data: Optional[Dict[str, Any]] = None) -> GenerationResult:
    return pipeline.generate_weather_announcement(hour=hour, minute=minute, dj=dj, weather_data=weather_data)


def generate_batch_weather_announcements(
    pipeline: GenerationPipeline,
    dj: str = "julie",
    weather_times: Optional[List[int]] = None,
    location: Optional[str] = None,
    resume: bool = False,
    progress_callback: Optional[Callable[[BatchProgress], None]] = None,
    two_phase: bool = False,
) -> Iterator[GenerationResult]:
    # Default to config WEATHER_TIMES
    from src.ai_radio.config import WEATHER_TIMES
    from src.ai_radio.services.weather import WeatherService

    times = weather_times or WEATHER_TIMES
    total = len(times)
    completed = 0
    failed = 0

    # TODO: Parse location string into lat/lon if provided
    weather_service = WeatherService()

    # Two-phase mode: generate all scripts first, then all audio
    if two_phase:
        # Phase 1: Generate all text scripts
        for hour in times:
            minute = 0
            current_slot = f"{hour:02d}-{minute:02d}"
            text_path = pipeline.output_dir / "weather" / dj / current_slot / f"{dj}_0.txt"
            
            if resume and text_path.exists():
                completed += 1
                if progress_callback:
                    progress_callback(BatchProgress(total=total, completed=completed, failed=failed, current_song=current_slot))
                continue
            
            # Fetch forecast weather for the target hour (not current weather)
            weather_data = weather_service.get_forecast_for_hour(hour)
            
            result = pipeline.generate_weather_announcement(hour=hour, minute=minute, dj=dj, weather_data=weather_data, text_only=True)
            if result.success:
                completed += 1
            else:
                failed += 1
            
            if progress_callback:
                progress_callback(BatchProgress(total=total, completed=completed, failed=failed, current_song=current_slot))
        
        # Reset counters for Phase 2
        completed = 0
        failed = 0
        
        # Phase 2: Generate all audio
        for hour in times:
            minute = 0
            current_slot = f"{hour:02d}-{minute:02d}"
            audio_path = pipeline.output_dir / "weather" / dj / current_slot / f"{dj}_0.wav"
            
            if resume and audio_path.exists():
                completed += 1
                yield GenerationResult(song_id=f"weather_{hour:02d}{minute:02d}", dj=dj, text=None, audio_path=audio_path, success=True, skipped=True)
                if progress_callback:
                    progress_callback(BatchProgress(total=total, completed=completed, failed=failed, current_song=current_slot))
                continue
            
            result = pipeline.generate_weather_announcement(hour=hour, minute=minute, dj=dj, audio_only=True)
            if result.success:
                completed += 1
            else:
                failed += 1
            
            if progress_callback:
                progress_callback(BatchProgress(total=total, completed=completed, failed=failed, current_song=current_slot))
            
            yield result
    else:
        # Original single-phase mode
        for hour in times:
            minute = 0
            current_slot = f"{hour:02d}-{minute:02d}"
            audio_path = pipeline.output_dir / "weather" / dj / current_slot / f"{dj}_0.wav"
            if resume and audio_path.exists():
                completed += 1
                yield GenerationResult(song_id=f"weather_{hour:02d}{minute:02d}", dj=dj, text=None, audio_path=audio_path, success=True, skipped=True)
                if progress_callback:
                    progress_callback(BatchProgress(total=total, completed=completed, failed=failed, current_song=current_slot))
                continue

            # Fetch forecast weather for the target hour (not current weather)
            weather_data = weather_service.get_forecast_for_hour(hour)

            result = pipeline.generate_weather_announcement(hour=hour, minute=minute, dj=dj, weather_data=weather_data)
            if result.success:
                completed += 1
            else:
                failed += 1

            if progress_callback:
                progress_callback(BatchProgress(total=total, completed=completed, failed=failed, current_song=current_slot))

            yield result


def generate_song_outro(pipeline: GenerationPipeline, song_id: str, artist: str, title: str, dj: str, next_song: str = None) -> GenerationResult:
    return pipeline.generate_song_outro(song_id=song_id, artist=artist, title=title, dj=dj, next_song=next_song)


def generate_batch_outros(
    pipeline: GenerationPipeline,
    songs: List[Dict[str, Any]],
    dj: str = "julie",
    resume: bool = False,
    progress_callback: Optional[Callable[[BatchProgress], None]] = None,
    two_phase: bool = False,
    enable_bridges: bool = False,
) -> Iterator[GenerationResult]:
    total = len(songs)
    completed = 0
    failed = 0

    # Two-phase mode: generate all scripts first, then all audio
    if two_phase:
        # Phase 1: Generate all text scripts
        for i, s in enumerate(songs):
            current_song = s.get("title") or s.get("id")
            safe_artist = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in s.get("artist", "Unknown"))
            safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in s.get("title", "Unknown"))
            safe_artist = safe_artist.strip().replace(' ', '_')
            safe_title = safe_title.strip().replace(' ', '_')
            folder_name = f"{safe_artist}-{safe_title}"
            text_path = pipeline.output_dir / "outros" / dj / folder_name / f"{dj}_outro.txt"
            
            if resume and text_path.exists():
                completed += 1
                if progress_callback:
                    progress_callback(BatchProgress(total=total, completed=completed, failed=failed, current_song=current_song))
                continue
            
            # Determine next song for bridge (if enabled)
            next_song_info = None
            if enable_bridges and i < len(songs) - 1:
                next_s = songs[i + 1]
                next_song_info = f"{next_s.get('title', 'Unknown')} by {next_s.get('artist', 'Unknown')}"
            
            result = pipeline.generate_song_outro(song_id=s["id"], artist=s.get("artist"), title=s.get("title"), dj=dj, next_song=next_song_info, text_only=True)
            if result.success:
                completed += 1
            else:
                failed += 1
            
            if progress_callback:
                progress_callback(BatchProgress(total=total, completed=completed, failed=failed, current_song=current_song))
        
        # Reset counters for Phase 2
        completed = 0
        failed = 0
        
        # Phase 2: Generate all audio
        for s in songs:
            current_song = s.get("title") or s.get("id")
            safe_artist = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in s.get("artist", "Unknown"))
            safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in s.get("title", "Unknown"))
            safe_artist = safe_artist.strip().replace(' ', '_')
            safe_title = safe_title.strip().replace(' ', '_')
            folder_name = f"{safe_artist}-{safe_title}"
            audio_path = pipeline.output_dir / "outros" / dj / folder_name / f"{dj}_outro.wav"
            
            if resume and audio_path.exists():
                completed += 1
                res = GenerationResult(song_id=s["id"], dj=dj, text=None, audio_path=audio_path, success=True, skipped=True)
                if progress_callback:
                    progress_callback(BatchProgress(total=total, completed=completed, failed=failed, current_song=current_song))
                yield res
                continue
            
            result = pipeline.generate_song_outro(song_id=s["id"], artist=s.get("artist"), title=s.get("title"), dj=dj, audio_only=True)
            if result.success:
                completed += 1
            else:
                failed += 1
            
            if progress_callback:
                progress_callback(BatchProgress(total=total, completed=completed, failed=failed, current_song=current_song))
            
            yield result
    else:
        # Original single-phase mode
        for i, s in enumerate(songs):
            current_song = s.get("title") or s.get("id")

            if resume:
                safe_artist = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in s.get("artist", "Unknown"))
                safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in s.get("title", "Unknown"))
                safe_artist = safe_artist.strip().replace(' ', '_')
                safe_title = safe_title.strip().replace(' ', '_')
                folder_name = f"{safe_artist}-{safe_title}"
                existing = pipeline.output_dir / "outros" / dj / folder_name / f"{dj}_outro.wav"
                if existing.exists():
                    completed += 1
                    res = GenerationResult(song_id=s["id"], dj=dj, text=None, audio_path=existing, success=True, skipped=True)
                    if progress_callback:
                        progress_callback(BatchProgress(total=total, completed=completed, failed=failed, current_song=current_song))
                    yield res
                    continue

            # Determine next song for bridge (if enabled)
            next_song_info = None
            if enable_bridges and i < len(songs) - 1:
                next_s = songs[i + 1]
                next_song_info = f"{next_s.get('title', 'Unknown')} by {next_s.get('artist', 'Unknown')}"

            result = pipeline.generate_song_outro(song_id=s["id"], artist=s.get("artist"), title=s.get("title"), dj=dj, next_song=next_song_info)
            if result.success:
                completed += 1
            else:
                failed += 1

            if progress_callback:
                progress_callback(BatchProgress(total=total, completed=completed, failed=failed, current_song=current_song))

            yield result
