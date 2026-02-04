import os
import tempfile
import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

logger = logging.getLogger(__name__)

# Supported video formats
SUPPORTED_FORMATS = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.m4v', '.mpg', '.mpeg'}

# Maximum file size (500MB)
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB in bytes


def validate_video_file(filename: str, file_size: int) -> tuple[bool, str]:
    """
    Validate video file format and size.
    
    Args:
        filename: Name of the uploaded file
        file_size: Size of the file in bytes
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check file extension
    file_ext = Path(filename).suffix.lower()
    if file_ext not in SUPPORTED_FORMATS:
        return False, f"Unsupported file format. Supported formats: {', '.join(SUPPORTED_FORMATS)}"
    
    # Check file size
    if file_size > MAX_FILE_SIZE:
        max_size_mb = MAX_FILE_SIZE / (1024 * 1024)
        return False, f"File size exceeds maximum limit of {max_size_mb:.0f}MB"
    
    return True, ""


@contextmanager
def temporary_file(suffix: str = "") -> Generator[Path, None, None]:
    """
    Context manager for creating and automatically cleaning up temporary files.
    
    Args:
        suffix: File extension (e.g., '.mp4', '.wav')
    
    Yields:
        Path object of the temporary file
    """
    temp_file = None
    try:
        # Create temporary file
        fd, temp_path = tempfile.mkstemp(suffix=suffix)
        os.close(fd)  # Close the file descriptor
        temp_file = Path(temp_path)
        logger.info(f"Created temporary file: {temp_file}")
        yield temp_file
    finally:
        # Cleanup
        if temp_file and temp_file.exists():
            try:
                temp_file.unlink()
                logger.info(f"Deleted temporary file: {temp_file}")
            except Exception as e:
                logger.error(f"Failed to delete temporary file {temp_file}: {e}")


@contextmanager
def temporary_directory() -> Generator[Path, None, None]:
    """
    Context manager for creating and automatically cleaning up temporary directories.
    
    Yields:
        Path object of the temporary directory
    """
    temp_dir = None
    try:
        temp_dir = Path(tempfile.mkdtemp())
        logger.info(f"Created temporary directory: {temp_dir}")
        yield temp_dir
    finally:
        # Cleanup
        if temp_dir and temp_dir.exists():
            try:
                import shutil
                shutil.rmtree(temp_dir)
                logger.info(f"Deleted temporary directory: {temp_dir}")
            except Exception as e:
                logger.error(f"Failed to delete temporary directory {temp_dir}: {e}")


def format_timestamp(seconds: float) -> str:
    """
    Format seconds into HH:MM:SS.mmm format for subtitles.
    
    Args:
        seconds: Time in seconds
    
    Returns:
        Formatted timestamp string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"


def generate_srt(segments: list[dict]) -> str:
    """
    Generate SRT subtitle format from Whisper segments.
    
    Args:
        segments: List of segment dictionaries with 'start', 'end', and 'text'
    
    Returns:
        SRT formatted string
    """
    srt_content = []
    for i, segment in enumerate(segments, 1):
        start_time = format_timestamp(segment['start'])
        end_time = format_timestamp(segment['end'])
        text = segment['text'].strip()
        
        srt_content.append(f"{i}")
        srt_content.append(f"{start_time.replace('.', ',')} --> {end_time.replace('.', ',')}")
        srt_content.append(text)
        srt_content.append("")  # Empty line between subtitles
    
    return "\n".join(srt_content)
