import asyncio
import logging
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from transcriber import model_is_loaded, transcribe_video
from utils import (
    MAX_FILE_SIZE,
    generate_srt,
    temporary_file,
    validate_video_file,
)

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="EchoScribe",
    description="Video transcription service using OpenAI Whisper",
    version="1.1.0",
)

DEFAULT_CORS = "http://localhost:8000,http://127.0.0.1:8000,null"
cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", DEFAULT_CORS).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEFAULT_MODEL = os.getenv("WHISPER_MODEL", "base")
VALID_MODELS = ["tiny", "base", "small", "medium", "large"]
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
CHUNK_SIZE = 1024 * 1024


class TranscriptionResponse(BaseModel):
    text: str
    language: str
    duration: float
    segments: list[dict]
    model_used: str


def _validate_model(model: str) -> None:
    if model not in VALID_MODELS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid model name. Choose from: {', '.join(VALID_MODELS)}",
        )


async def _save_upload(file: UploadFile, destination: Path) -> int:
    total = 0
    with destination.open("wb") as buffer:
        while True:
            chunk = await file.read(CHUNK_SIZE)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File size exceeds maximum limit of {MAX_FILE_SIZE / (1024 * 1024):.0f}MB",
                )
            buffer.write(chunk)
    return total


async def transcribe_upload(
    file: UploadFile,
    model: str,
    language: Optional[str],
) -> dict:
    filename = file.filename or ""
    _validate_model(model)

    is_valid, error_message = validate_video_file(filename, 0)
    if not is_valid:
        logger.warning("Invalid file: %s", error_message)
        raise HTTPException(status_code=400, detail=error_message)

    file_ext = Path(filename).suffix
    with temporary_file(suffix=file_ext) as temp_video_path:
        logger.info("Saving uploaded file to %s", temp_video_path)
        size = await _save_upload(file, temp_video_path)
        if size == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        logger.info("Starting transcription with model: %s", model)
        result = await asyncio.to_thread(
            transcribe_video,
            temp_video_path,
            model,
            language,
        )
        result["model_used"] = model
        logger.info("Transcription successful: %s characters", len(result["text"]))
        return result


@app.get("/api")
async def api_info():
    return {
        "service": "EchoScribe",
        "status": "running",
        "version": "1.1.0",
        "description": "Video transcription service using OpenAI Whisper",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": model_is_loaded(),
    }


@app.get("/models")
async def list_models():
    return {
        "models": [
            {"name": "tiny", "description": "Fastest, least accurate (~1GB RAM)", "size": "39M"},
            {"name": "base", "description": "Good balance (default)", "size": "74M"},
            {"name": "small", "description": "Better accuracy", "size": "244M"},
            {"name": "medium", "description": "High accuracy", "size": "769M"},
            {"name": "large", "description": "Best accuracy, slowest", "size": "1550M"},
        ],
        "default": DEFAULT_MODEL,
    }


@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe(
    file: UploadFile = File(..., description="Video file to transcribe"),
    model: str = Form(default=DEFAULT_MODEL, description="Whisper model to use"),
    language: Optional[str] = Form(default=None, description="Language code (optional)"),
):
    """Transcribe a video file to text with timestamped segments."""
    logger.info("Received transcription request: file=%s, model=%s", file.filename, model)
    try:
        result = await transcribe_upload(file, model, language)
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Transcription error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    finally:
        await file.close()


@app.post("/transcribe/srt")
async def transcribe_to_srt(
    file: UploadFile = File(..., description="Video file to transcribe"),
    model: str = Form(default=DEFAULT_MODEL, description="Whisper model to use"),
    language: Optional[str] = Form(default=None, description="Language code (optional)"),
):
    """Transcribe a video file and return SRT subtitle format."""
    logger.info("Received SRT transcription request: file=%s, model=%s", file.filename, model)
    try:
        result = await transcribe_upload(file, model, language)
        return JSONResponse(
            content={
                "srt": generate_srt(result["segments"]),
                "language": result["language"],
                "duration": result["duration"],
                "model_used": result["model_used"],
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("SRT transcription error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    finally:
        await file.close()


if FRONTEND_DIR.exists():
    app.mount(
        "/",
        StaticFiles(directory=str(FRONTEND_DIR), html=True),
        name="frontend",
    )
else:
    logger.warning("Frontend directory not found at %s", FRONTEND_DIR)


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)
