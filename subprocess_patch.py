"""
Windows subprocess window suppression patch.

This module patches Python's subprocess module to automatically suppress
console windows on Windows when spawning subprocesses. This is critical
for preventing flickering terminal windows when pydub calls ffmpeg.

The patch works by:
1. Intercepting subprocess.Popen and subprocess.run calls
2. Automatically adding CREATE_NO_WINDOW flag on Windows
3. Adding STARTUPINFO with SW_HIDE for additional suppression
4. Ensuring the patch is applied before any subprocess calls are made

This solution is robust under slow CPU conditions because:
- Flags are set at process creation time (synchronous with CreateProcess)
- No race condition between window creation and suppression
- Works even when process creation is delayed
"""

import sys
import subprocess
from functools import wraps

# Windows-specific constants
if sys.platform == 'win32':
    import ctypes
    from ctypes import wintypes
    
    # Windows API constants
    CREATE_NO_WINDOW = 0x08000000
    STARTF_USESHOWWINDOW = 0x00000001
    SW_HIDE = 0
    
    # Store original functions
    _original_popen = subprocess.Popen
    _original_run = subprocess.run
    _original_call = subprocess.call
    _original_check_call = subprocess.check_call
    _original_check_output = subprocess.check_output


def _get_windows_startupinfo():
    """
    Create a STARTUPINFO structure that hides the console window.
    This is used in addition to CREATE_NO_WINDOW for maximum suppression.
    """
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = SW_HIDE
    return startupinfo


def _patch_popen_kwargs(kwargs):
    """
    Patch keyword arguments for subprocess.Popen to suppress windows.
    
    Args:
        kwargs: Dictionary of keyword arguments passed to Popen
        
    Modifies kwargs in-place to add window suppression flags.
    """
    if sys.platform != 'win32':
        return
    
    # Add CREATE_NO_WINDOW to creationflags
    if 'creationflags' not in kwargs:
        kwargs['creationflags'] = 0
    kwargs['creationflags'] |= CREATE_NO_WINDOW
    
    # Add STARTUPINFO to hide window
    if 'startupinfo' not in kwargs:
        kwargs['startupinfo'] = _get_windows_startupinfo()
    else:
        # If startupinfo is already provided, enhance it
        si = kwargs['startupinfo']
        if si is None:
            si = _get_windows_startupinfo()
        else:
            si.dwFlags |= STARTF_USESHOWWINDOW
            si.wShowWindow = SW_HIDE
        kwargs['startupinfo'] = si


@wraps(_original_popen)
def _patched_popen(*args, **kwargs):
    """Patched version of subprocess.Popen with window suppression."""
    _patch_popen_kwargs(kwargs)
    return _original_popen(*args, **kwargs)


@wraps(_original_run)
def _patched_run(*args, **kwargs):
    """Patched version of subprocess.run with window suppression."""
    _patch_popen_kwargs(kwargs)
    return _original_run(*args, **kwargs)


@wraps(_original_call)
def _patched_call(*args, **kwargs):
    """Patched version of subprocess.call with window suppression."""
    _patch_popen_kwargs(kwargs)
    return _original_call(*args, **kwargs)


@wraps(_original_check_call)
def _patched_check_call(*args, **kwargs):
    """Patched version of subprocess.check_call with window suppression."""
    _patch_popen_kwargs(kwargs)
    return _original_check_call(*args, **kwargs)


@wraps(_original_check_output)
def _patched_check_output(*args, **kwargs):
    """Patched version of subprocess.check_output with window suppression."""
    _patch_popen_kwargs(kwargs)
    return _original_check_output(*args, **kwargs)


def apply_patch():
    """
    Apply the subprocess patch to suppress console windows.
    
    This function should be called as early as possible in the application,
    ideally before importing pydub or any other module that uses subprocess.
    
    The patch is idempotent - calling it multiple times is safe.
    """
    if sys.platform != 'win32':
        return  # Only needed on Windows
    
    # Apply patches
    subprocess.Popen = _patched_popen
    subprocess.run = _patched_run
    subprocess.call = _patched_call
    subprocess.check_call = _patched_check_call
    subprocess.check_output = _patched_check_output


def remove_patch():
    """
    Remove the subprocess patch and restore original functions.
    
    This is mainly for testing purposes. In production, the patch
    should remain active for the lifetime of the application.
    """
    if sys.platform != 'win32':
        return
    
    subprocess.Popen = _original_popen
    subprocess.run = _original_run
    subprocess.call = _original_call
    subprocess.check_call = _original_check_call
    subprocess.check_output = _original_check_output


# Auto-apply patch when module is imported (on Windows)
if sys.platform == 'win32':
    apply_patch()

