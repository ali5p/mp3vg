"""
Text-to-speech engine using gTTS and audio processing with pydub.
"""

# CRITICAL: Import subprocess patch BEFORE any other imports that use subprocess
# This ensures all subprocess calls (including those from pydub) are patched
import subprocess_patch  # noqa: F401

import os
import shutil
import tempfile
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional, Callable
from gtts import gTTS
from pydub import AudioSegment
from pydub.effects import normalize
from utils import check_ffmpeg_available


@dataclass
class LanguagePairConfig:
    """
    Configuration for language pair sequencing and pause settings.
    
    Attributes:
        sequence: List of language codes in playback order (e.g., ["cs", "en"] or ["en", "cs"])
        pause_within_pair: Pause duration in seconds between items in the sequence
        pause_between_pairs: Pause duration in seconds between word pairs
    """
    sequence: List[str]
    pause_within_pair: float
    pause_between_pairs: float


def setup_ffmpeg_path():
    """
    Setup ffmpeg path for pydub to use local portable version.
    For PyInstaller builds, looks for ffmpeg next to the executable.
    For development, looks for ffmpeg in project folder.
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable (PyInstaller)
        # Look for ffmpeg next to the .exe file
        exe_path = Path(sys.executable)
        base_path = exe_path.parent
    else:
        # Running as script - look in project folder
        base_path = Path(__file__).parent
    
    # Path to local ffmpeg (next to executable or in project folder)
    ffmpeg_dir = base_path / "ffmpeg" / "bin"
    ffmpeg_exe = ffmpeg_dir / "ffmpeg.exe"
    
    # Check if local ffmpeg exists
    if ffmpeg_exe.exists():
        # Convert to absolute path
        ffmpeg_exe_abs = ffmpeg_exe.resolve()
        ffprobe_exe_abs = (ffmpeg_dir / "ffprobe.exe").resolve()
        
        # Set pydub to use local ffmpeg
        ffmpeg_path_str = str(ffmpeg_exe_abs)
        AudioSegment.converter = ffmpeg_path_str
        AudioSegment.ffmpeg = ffmpeg_path_str
        if ffprobe_exe_abs.exists():
            AudioSegment.ffprobe = str(ffprobe_exe_abs)
        
        # Also set the environment variable for subprocess calls
        import os
        os.environ['PATH'] = str(ffmpeg_dir.resolve()) + os.pathsep + os.environ.get('PATH', '')
        
        return True
    
    return False


# Setup ffmpeg path when module is imported
_ffmpeg_available = setup_ffmpeg_path()


class TTSEngine:
    """Handles text-to-speech generation and audio concatenation."""
    
    def __init__(self):
        """Initialize the TTS engine."""
        self.temp_dir = None
        
    def _create_temp_dir(self) -> Path:
        """Create a temporary directory for storing intermediate audio files."""
        if self.temp_dir is None:
            self.temp_dir = Path(tempfile.mkdtemp(prefix="mp3vg_"))
        return self.temp_dir
    
    def _cleanup_temp_dir(self):
        """Clean up temporary directory and files."""
        if self.temp_dir and self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir)
            except Exception:
                pass  # Ignore cleanup errors
            self.temp_dir = None
    
    def generate_speech(self, text: str, language: str, output_path: Path) -> Path:
        """
        Generate speech audio file from text using gTTS.
        
        Args:
            text: Text to convert to speech
            language: Language code (e.g., 'cs', 'en', 'ru', etc.)
            output_path: Path where the audio file should be saved
            
        Returns:
            Path to the generated audio file
            
        Raises:
            Exception: If TTS generation fails
        """
        try:
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(str(output_path))
            return output_path
        except Exception as e:
            raise Exception(f"Failed to generate speech for '{text}': {str(e)}")
    
    def create_silence(self, duration_ms: int) -> AudioSegment:
        """
        Create a silent audio segment of specified duration.
        
        Args:
            duration_ms: Duration in milliseconds
            
        Returns:
            AudioSegment representing silence
        """
        return AudioSegment.silent(duration=duration_ms)
    
    def concatenate_audio(self, audio_segments: List[AudioSegment]) -> AudioSegment:
        """
        Concatenate multiple audio segments into one.
        
        Args:
            audio_segments: List of AudioSegment objects to concatenate
            
        Returns:
            Combined AudioSegment
        """
        if not audio_segments:
            return AudioSegment.silent(duration=0)
        
        combined = audio_segments[0]
        for segment in audio_segments[1:]:
            combined += segment
        
        return combined
    
    def generate_lesson_audio(
        self,
        word_pairs: List[Tuple[str, str]],
        config: LanguagePairConfig,
        output_path: Path,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Path:
        """
        Generate complete MP3 lesson from word pairs using configurable language sequence.
        
        Args:
            word_pairs: List of (L1_word, L2_word) tuples
                       - word_pairs[0] is always L1_word, uses profile.sequence[0] language
                       - word_pairs[1] is always L2_word, uses profile.sequence[1] language
            config: LanguagePairConfig containing sequence, pause settings, and role_order
            output_path: Path where the final MP3 should be saved
            progress_callback: Optional callback function(status_message) for progress updates
            
        Returns:
            Path to the generated MP3 file
            
        Raises:
            Exception: If generation fails at any step
        """
        # Get role order (determines playback sequence)
        # role_order is a list like [0, 1] for L1→L2, [1, 0] for L2→L1, or [1, 0, 1] for L2→L1→L2
        role_order = getattr(config, 'role_order', [0, 1])  # Default to L1→L2 if not set
        
        # Validate sequence length matches role order length
        if len(config.sequence) != len(role_order):
            raise ValueError(
                f"Sequence length ({len(config.sequence)}) must match role order length ({len(role_order)})"
            )
        
        # Validate that we have at least 2 roles (L1 and L2)
        if len(role_order) < 2:
            raise ValueError(f"Role order must contain at least 2 roles, got {len(role_order)}")
        
        # Validate that role indices are valid (0 for L1, 1 for L2)
        valid_roles = {0, 1}
        invalid_roles = set(role_order) - valid_roles
        if invalid_roles:
            raise ValueError(f"Invalid role indices in role_order: {invalid_roles}. Valid roles are 0 (L1) and 1 (L2)")
        
        # Map roles to their language codes and word indices
        # Words are invariantly bound to roles:
        # - word_pairs[0] is always L1_word, uses L1 language
        # - word_pairs[1] is always L2_word, uses L2 language
        # Playback order only changes sequence, not word-to-language mapping
        
        role_to_word_index = {0: 0, 1: 1}  # L1 role -> word 0, L2 role -> word 1
        
        # Get original profile sequence to map roles to languages
        # profile_sequence[0] is L1 language, profile_sequence[1] is L2 language
        profile_sequence = getattr(config, 'profile_sequence', config.sequence)
        role_to_language = {
            0: profile_sequence[0],  # L1 role -> L1 language
            1: profile_sequence[1]   # L2 role -> L2 language
        }
        
        # Check for ffmpeg availability (must be local, next to executable)
        if getattr(sys, 'frozen', False):
            exe_path = Path(sys.executable)
            base_path = exe_path.parent
        else:
            base_path = Path(__file__).parent
        
        local_ffmpeg_path = base_path / "ffmpeg" / "bin" / "ffmpeg.exe"
        
        if not setup_ffmpeg_path():
            raise Exception(
                f"FFmpeg not found!\n\n"
                f"Please place ffmpeg next to the executable:\n"
                f"{local_ffmpeg_path.parent}\n\n"
                f"Expected file: {local_ffmpeg_path}\n\n"
                f"Download from: https://www.gyan.dev/ffmpeg/builds/\n"
                f"Extract the 'bin' folder contents to 'ffmpeg/bin' folder."
            )
        
        temp_dir = self._create_temp_dir()
        audio_segments = []
        
        try:
            total_pairs = len(word_pairs)
            
            if progress_callback:
                progress_callback(f"Starting generation of {total_pairs} word pairs...")
            
            # Convert pause durations to milliseconds
            pause_within_ms = int(config.pause_within_pair * 1000)
            pause_between_ms = int(config.pause_between_pairs * 1000)
            
            for idx, word_pair in enumerate(word_pairs, start=1):
                # Build display string for progress
                word_display = " → ".join(word_pair)
                if progress_callback:
                    progress_callback(f"Processing pair {idx}/{total_pairs}: {word_display}")
                
                # Generate audio for each role in playback order
                # Words are bound to roles: word_pair[0] is L1_word, word_pair[1] is L2_word
                # Each role has its own language that never changes
                pair_audio_segments = []
                
                for playback_idx, role_idx in enumerate(role_order):
                    # Get word index for this role (L1 role -> 0, L2 role -> 1)
                    word_index = role_to_word_index[role_idx]
                    # Get language code for this role
                    lang_code = role_to_language[role_idx]
                    # Get the word for this role
                    word = word_pair[word_index]
                    
                    # Generate speech audio
                    audio_path = temp_dir / f"lang_{lang_code}_{idx}.mp3"
                    self.generate_speech(word, lang_code, audio_path)
                    
                    # Ensure ffmpeg is set before loading audio
                    setup_ffmpeg_path()
                    audio = AudioSegment.from_mp3(str(audio_path))
                    pair_audio_segments.append(audio)
                    
                    # Add pause between roles in playback order (except after the last one)
                    if playback_idx < len(role_order) - 1:
                        pair_audio_segments.append(self.create_silence(pause_within_ms))
                
                # Combine all audio segments for this pair
                pair_audio = pair_audio_segments[0]
                for segment in pair_audio_segments[1:]:
                    pair_audio += segment
                
                # Normalize audio for consistent volume
                pair_audio = normalize(pair_audio)
                
                audio_segments.append(pair_audio)
                
                # Add pause between pairs (except after the last one)
                if idx < total_pairs:
                    audio_segments.append(self.create_silence(pause_between_ms))
            
            if progress_callback:
                progress_callback("Concatenating all audio segments...")
            
            # Concatenate all segments
            final_audio = self.concatenate_audio(audio_segments)
            
            if progress_callback:
                progress_callback(f"Exporting to MP3: {output_path}")
            
            # Ensure ffmpeg is set before exporting
            setup_ffmpeg_path()
            
            # Export to MP3
            final_audio.export(str(output_path), format="mp3", bitrate="192k")
            
            if progress_callback:
                progress_callback(f"✓ Successfully generated: {output_path}")
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Failed to generate lesson audio: {str(e)}")
        finally:
            # Clean up temporary files
            self._cleanup_temp_dir()
    
    def __del__(self):
        """Cleanup on destruction."""
        self._cleanup_temp_dir()
