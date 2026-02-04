import os
import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from transcriber import transcribe_video
from utils import validate_video_file, temporary_file, generate_srt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="EchoScribe",
    description="Video transcription service using OpenAI Whisper",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get model name from environment variable
DEFAULT_MODEL = os.getenv("WHISPER_MODEL", "base")


class TranscriptionResponse(BaseModel):
    """Response model for transcription endpoint"""
    text: str
    language: str
    duration: float
    segments: list[dict]
    model_used: str


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "service": "EchoScribe",
        "status": "running",
        "version": "1.0.0",
        "description": "Video transcription service using OpenAI Whisper"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/models")
async def list_models():
    """List available Whisper models"""
    return {
        "models": [
            {"name": "tiny", "description": "Fastest, least accurate (~1GB RAM)", "size": "39M"},
            {"name": "base", "description": "Good balance (default)", "size": "74M"},
            {"name": "small", "description": "Better accuracy", "size": "244M"},
            {"name": "medium", "description": "High accuracy", "size": "769M"},
            {"name": "large", "description": "Best accuracy, slowest", "size": "1550M"}
        ],
        "default": DEFAULT_MODEL
    }


@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe(
    file: UploadFile = File(..., description="Video file to transcribe"),
    model: str = Form(default=DEFAULT_MODEL, description="Whisper model to use"),
    language: Optional[str] = Form(default=None, description="Language code (optional)")
):
    """
    Transcribe a video file to text.
    
    - **file**: Video file to transcribe (mp4, avi, mov, mkv, etc.)
    - **model**: Whisper model to use (tiny, base, small, medium, large)
    - **language**: Optional language code (e.g., 'en', 'es', 'fr')
    
    Returns transcription text, segments with timestamps, detected language, and duration.
    """
    logger.info(f"Received transcription request: file={file.filename}, model={model}")
    
    try:
        # Read file content (UploadFile.seek() doesn't support whence, so we read first)
        content = await file.read()
        file_size = len(content)
        
        # Validate file
        is_valid, error_message = validate_video_file(file.filename, file_size)
        if not is_valid:
            logger.warning(f"Invalid file: {error_message}")
            raise HTTPException(status_code=400, detail=error_message)
        
        # Validate model name
        valid_models = ["tiny", "base", "small", "medium", "large"]
        if model not in valid_models:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid model name. Choose from: {', '.join(valid_models)}"
            )
        
        # Save uploaded file to temporary location
        file_ext = Path(file.filename).suffix
        with temporary_file(suffix=file_ext) as temp_video_path:
            # Write uploaded file to temporary file
            logger.info(f"Saving uploaded file to {temp_video_path}")
            temp_video_path.write_bytes(content)
            
            # Transcribe video
            logger.info(f"Starting transcription with model: {model}")
            result = transcribe_video(temp_video_path, model_name=model, language=language)
            
            logger.info(f"Transcription successful: {len(result['text'])} characters")
            
            # Add model info to response
            result["model_used"] = model
            
            return JSONResponse(content=result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    finally:
        await file.close()


@app.post("/transcribe/srt")
async def transcribe_to_srt(
    file: UploadFile = File(..., description="Video file to transcribe"),
    model: str = Form(default=DEFAULT_MODEL, description="Whisper model to use"),
    language: Optional[str] = Form(default=None, description="Language code (optional)")
):
    """
    Transcribe a video file and return SRT subtitle format.
    
    - **file**: Video file to transcribe
    - **model**: Whisper model to use
    - **language**: Optional language code
    
    Returns transcription in SRT subtitle format.
    """
    logger.info(f"Received SRT transcription request: file={file.filename}, model={model}")
    
    try:
        # Read file content (UploadFile.seek() doesn't support whence, so we read first)
        content = await file.read()
        file_size = len(content)
        
        # Validate file
        is_valid, error_message = validate_video_file(file.filename, file_size)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        # Validate model name
        valid_models = ["tiny", "base", "small", "medium", "large"]
        if model not in valid_models:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid model name. Choose from: {', '.join(valid_models)}"
            )
        
        # Save uploaded file to temporary location
        file_ext = Path(file.filename).suffix
        with temporary_file(suffix=file_ext) as temp_video_path:
            temp_video_path.write_bytes(content)
            
            # Transcribe video
            result = transcribe_video(temp_video_path, model_name=model, language=language)
            
            # Generate SRT format
            srt_content = generate_srt(result["segments"])
            
            return JSONResponse(content={
                "srt": srt_content,
                "language": result["language"],
                "duration": result["duration"],
                "model_used": model
            })
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"SRT transcription error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    finally:
        await file.close()


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
