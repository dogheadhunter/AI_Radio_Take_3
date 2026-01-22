"""Generation pipeline that orchestrates LLM -> TTS."""
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Callable, Optional, List, Dict, Any
from src.ai_radio.generation.llm_client import LLMClient, generate_text
from src.ai_radio.generation.tts_client import TTSClient, generate_audio
from src.ai_radio.generation.prompts import build_song_intro_prompt, DJ
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
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path("data/generated")
        self._llm_loaded = False
        self._tts_loaded = False
        self._llm = LLMClient()
        self._tts = TTSClient()

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

    def generate_song_intro(self, song_id: str, artist: str, title: str, dj: str) -> GenerationResult:
        try:
            # Create song folder
            song_folder = self._make_song_folder(song_id, artist, title, dj)
            
            # Generate text
            self._llm_loaded = True
            prompt = build_song_intro_prompt(DJ(dj), artist=artist, title=title)
            text = generate_text(self._llm, prompt)
            self._llm_loaded = False

            # Save text script
            text_path = song_folder / f"{dj}_0.txt"
            text_path.write_text(text, encoding='utf-8')
            
            # Generate audio
            audio_path = song_folder / f"{dj}_0.wav"
            
            # Use voice reference if available
            voice_ref = VOICE_REFERENCES_DIR / f"{dj}.wav"
            if not voice_ref.exists():
                voice_ref = None
            
            generate_audio(self._tts, text=text, output_path=audio_path, voice_reference=voice_ref)

            return GenerationResult(song_id=song_id, dj=dj, text=text, audio_path=audio_path, success=True)
        except Exception as exc:
            return GenerationResult(song_id=song_id, dj=dj, text=None, audio_path=None, success=False, error=str(exc))

    def generate_batch_intros(
        self,
        songs: List[Dict[str, Any]],
        dj: str = "julie",
        resume: bool = False,
        progress_callback: Optional[Callable[[BatchProgress], None]] = None,
    ) -> Iterator[GenerationResult]:
        total = len(songs)
        completed = 0
        failed = 0

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

            result = self.generate_song_intro(s["id"], artist=s.get("artist"), title=s.get("title"), dj=dj)
            if result.success:
                completed += 1
            else:
                failed += 1

            if progress_callback:
                progress_callback(BatchProgress(total=total, completed=completed, failed=failed, current_song=current_song))

            yield result


def generate_song_intro(pipeline: GenerationPipeline, song_id: str, artist: str, title: str, dj: str) -> GenerationResult:
    """Module-level helper function that delegates to a pipeline instance."""
    return pipeline.generate_song_intro(song_id=song_id, artist=artist, title=title, dj=dj)


def generate_batch_intros(
    pipeline: GenerationPipeline,
    songs: List[Dict[str, Any]],
    dj: str = "julie",
    resume: bool = False,
    progress_callback: Optional[Callable[[BatchProgress], None]] = None,
) -> Iterator[GenerationResult]:
    return pipeline.generate_batch_intros(songs, dj=dj, resume=resume, progress_callback=progress_callback)
