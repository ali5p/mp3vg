"""
Utility functions for parsing and validating word pairs input.
"""

import re
import shutil
import sys
from pathlib import Path
from typing import List, Tuple, Optional


def parse_word_pairs(text: str) -> List[Tuple[str, str]]:
    """
    Parse word pairs from text input.
    
    Expected format: One pair per line, separated by comma
    Example:
        word1,word2
        first,second
    
    Args:
        text: Raw text input from the text area
        
    Returns:
        List of tuples (first_word, second_word)
        
    Raises:
        ValueError: If format is invalid
    """
    if not text or not text.strip():
        raise ValueError("Input is empty. Please enter at least one word pair.")
    
    pairs = []
    lines = text.strip().split('\n')
    
    for line_num, line in enumerate(lines, start=1):
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Split by comma
        parts = [part.strip() for part in line.split(',', 1)]
        
        if len(parts) != 2:
            raise ValueError(
                f"Invalid format on line {line_num}: '{line}'\n"
                f"Expected format: word1,word2 (one pair per line)"
            )
        
        first_word, second_word = parts
        
        if not first_word:
            raise ValueError(f"First word is missing on line {line_num}")
        if not second_word:
            raise ValueError(f"Second word is missing on line {line_num}")
        
        pairs.append((first_word, second_word))
    
    if not pairs:
        raise ValueError("No valid word pairs found. Please enter at least one pair.")
    
    return pairs


def validate_pause_duration(value: float, min_val: float = 0.0, max_val: float = 10.0) -> float:
    """
    Validate and clamp pause duration value.
    
    Args:
        value: Pause duration in seconds
        min_val: Minimum allowed value (default: 0.0)
        max_val: Maximum allowed value (default: 10.0)
        
    Returns:
        Clamped value within valid range
    """
    return max(min_val, min(max_val, value))


def format_time(seconds: float) -> str:
    """
    Format time duration as a readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string (e.g., "1.1s", "1.7s")
    """
    return f"{seconds:.1f}s"


def check_ffmpeg_available() -> Tuple[bool, str]:
    """
    Check if ffmpeg is available in the system PATH.
    This is used as a fallback if local ffmpeg is not found.
    
    Returns:
        Tuple of (is_available, error_message)
        - is_available: True if ffmpeg is found, False otherwise
        - error_message: Empty string if available, error message otherwise
    """
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path is None:
        return False, (
            "ffmpeg is not installed or not in your system PATH.\n\n"
            "Please install ffmpeg:\n"
            "1. Using Chocolatey: choco install ffmpeg\n"
            "2. Or download from: https://ffmpeg.org/download.html\n"
            "3. Add ffmpeg to your system PATH\n"
            "4. Restart the application after installation"
        )
    return True, ""


def check_local_ffmpeg() -> Tuple[bool, Optional[Path]]:
    """
    Check if local portable ffmpeg exists next to executable or in project folder.
    
    Returns:
        Tuple of (is_available, ffmpeg_path)
        - is_available: True if local ffmpeg is found
        - ffmpeg_path: Path to ffmpeg.exe if found, None otherwise
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable (PyInstaller)
        # Look for ffmpeg next to the .exe file
        exe_path = Path(sys.executable)
        base_path = exe_path.parent
    else:
        # Running as script - look in project folder
        base_path = Path(__file__).parent
    
    ffmpeg_exe = base_path / "ffmpeg" / "bin" / "ffmpeg.exe"
    if ffmpeg_exe.exists():
        return True, ffmpeg_exe
    return False, None
