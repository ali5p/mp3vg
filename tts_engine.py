"""
Text-to-speech engine using gTTS and audio processing with pydub.
"""

import os
import shutil
import tempfile
import sys
from pathlib import Path
from typing import List, Tuple, Optional, Callable
from gtts import gTTS
from pydub import AudioSegment
from pydub.effects import normalize
from utils import check_ffmpeg_available


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
            language: Language code ('cs' for Czech, 'en' for English)
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
        pause_within_pair: float,
        pause_between_pairs: float,
        output_path: Path,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Path:
        """
        Generate complete MP3 lesson from word pairs.
        
        Args:
            word_pairs: List of (Czech_word, English_word) tuples
            pause_within_pair: Pause duration in seconds between Czech and English
            pause_between_pairs: Pause duration in seconds between pairs
            output_path: Path where the final MP3 should be saved
            progress_callback: Optional callback function(status_message) for progress updates
            
        Returns:
            Path to the generated MP3 file
            
        Raises:
            Exception: If generation fails at any step
        """
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
            pause_within_ms = int(pause_within_pair * 1000)
            pause_between_ms = int(pause_between_pairs * 1000)
            
            for idx, (czech_word, english_word) in enumerate(word_pairs, start=1):
                if progress_callback:
                    progress_callback(f"Processing pair {idx}/{total_pairs}: {czech_word} → {english_word}")
                
                # Generate Czech audio
                czech_audio_path = temp_dir / f"czech_{idx}.mp3"
                self.generate_speech(czech_word, "cs", czech_audio_path)
                
                # Ensure ffmpeg is set before loading audio
                setup_ffmpeg_path()
                czech_audio = AudioSegment.from_mp3(str(czech_audio_path))
                
                # Generate English audio
                english_audio_path = temp_dir / f"english_{idx}.mp3"
                self.generate_speech(english_word, "en", english_audio_path)
                english_audio = AudioSegment.from_mp3(str(english_audio_path))
                
                # Combine Czech + pause + English
                pair_audio = czech_audio + self.create_silence(pause_within_ms) + english_audio
                
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
