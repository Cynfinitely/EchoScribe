import os
import logging
from pathlib import Path
from typing import Optional
import whisper
import ffmpeg

from utils import temporary_file

logger = logging.getLogger(__name__)

# Global variable to store loaded model
_model: Optional[whisper.Whisper] = None
_model_name: str = "base"


def model_is_loaded() -> bool:
    """Return whether a Whisper model is currently cached in memory."""
    return _model is not None


def get_model(model_name: str = "base") -> whisper.Whisper:
    """
    Load and cache the Whisper model.
    
    Args:
        model_name: Name of the Whisper model (tiny, base, small, medium, large)
    
    Returns:
        Loaded Whisper model
    """
    global _model, _model_name
    
    # Load model if not cached or if different model requested
    if _model is None or _model_name != model_name:
        logger.info(f"Loading Whisper model: {model_name}")
        _model = whisper.load_model(model_name)
        _model_name = model_name
        logger.info(f"Model {model_name} loaded successfully")
    
    return _model


def extract_audio(video_path: Path, audio_path: Path) -> None:
    """
    Extract audio from video file using FFmpeg.
    
    Args:
        video_path: Path to the input video file
        audio_path: Path to save the extracted audio
    
    Raises:
        Exception: If audio extraction fails
    """
    try:
        logger.info(f"Extracting audio from {video_path}")
        
        # Extract audio using ffmpeg-python
        stream = ffmpeg.input(str(video_path))
        stream = ffmpeg.output(stream, str(audio_path), acodec='pcm_s16le', ac=1, ar='16k')
        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
        
        logger.info(f"Audio extracted successfully to {audio_path}")
    except ffmpeg.Error as e:
        error_message = e.stderr.decode() if e.stderr else str(e)
        logger.error("FFmpeg error during audio extraction: %s", error_message)
        raise Exception(
            "Could not extract audio from this file. Check that it is a valid video."
        )


def transcribe_video(video_path: Path, model_name: str = "base", language: Optional[str] = None) -> dict:
    """
    Transcribe video file using Whisper.
    
    Args:
        video_path: Path to the video file
        model_name: Whisper model to use
        language: Optional language code (e.g., 'en', 'es', 'fr')
    
    Returns:
        Dictionary containing:
            - text: Full transcription text
            - segments: List of segments with timestamps
            - language: Detected language
            - duration: Audio duration in seconds
    
    Raises:
        Exception: If transcription fails
    """
    try:
        # Load model
        model = get_model(model_name)
        
        # Extract audio to temporary file
        with temporary_file(suffix='.wav') as audio_path:
            extract_audio(video_path, audio_path)
            
            # Transcribe audio
            logger.info(f"Starting transcription with model: {model_name}")
            
            # Prepare transcription options
            transcribe_options = {
                "fp16": False,  # Use FP32 for better compatibility
                "verbose": False
            }
            
            if language:
                transcribe_options["language"] = language
            
            # Perform transcription
            result = model.transcribe(str(audio_path), **transcribe_options)
            
            logger.info(f"Transcription completed. Detected language: {result.get('language', 'unknown')}")
            
            # Extract relevant information
            return {
                "text": result["text"].strip(),
                "segments": [
                    {
                        "start": segment["start"],
                        "end": segment["end"],
                        "text": segment["text"]
                    }
                    for segment in result.get("segments", [])
                ],
                "language": result.get("language", "unknown"),
                "duration": result.get("segments", [{}])[-1].get("end", 0) if result.get("segments") else 0
            }
    
    except Exception as e:
        logger.error("Transcription failed: %s", e)
        raise
