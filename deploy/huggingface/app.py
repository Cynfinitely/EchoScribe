"""
EchoScribe - Video Transcription with Whisper
Hugging Face Spaces Deployment (Gradio UI)

Standalone: it does not import backend/. Deploy guide: DEPLOY_FREE.md.
"""

import logging
import os
import tempfile
import time
from pathlib import Path
from typing import Optional

import ffmpeg
import gradio as gr
import whisper

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("echoscribe")

MODELS = ["tiny", "base", "small", "medium", "large"]
LANGUAGES = ["Auto-detect", "en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja", "ko", "ar", "hi", "tr"]

# Gradio keeps uploads and the TXT/SRT downloads in its cache. Every 15 minutes,
# delete cached files older than an hour so nothing outlives a session.
CACHE_SWEEP_SECONDS = 15 * 60
CACHE_MAX_AGE_SECONDS = 60 * 60
DOWNLOAD_DIR = Path(tempfile.mkdtemp(prefix="echoscribe-downloads-"))

# Load model (cached after first load)
_model_name = os.getenv("WHISPER_MODEL", "base")
logger.info("Loading Whisper model: %s", _model_name)
_model = whisper.load_model(_model_name)


def get_model(name: str) -> whisper.Whisper:
    """Return the requested Whisper model, loading it if it isn't the cached one."""
    global _model, _model_name
    if name != _model_name:
        logger.info("Switching to model: %s", name)
        _model = whisper.load_model(name)
        _model_name = name
    return _model


def format_timestamp(seconds: float) -> str:
    """Format seconds to HH:MM:SS,mmm for SRT format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}".replace(".", ",")


def generate_srt(segments: list) -> str:
    """Generate SRT subtitle format from segments."""
    srt_lines = []
    for i, seg in enumerate(segments, 1):
        start = format_timestamp(seg["start"])
        end = format_timestamp(seg["end"])
        text = seg["text"].strip()
        srt_lines.append(f"{i}\n{start} --> {end}\n{text}\n")
    return "\n".join(srt_lines)


def transcribe_video(video_path: Optional[str], model_choice: str, language: str):
    """
    Transcribe a video file using Whisper.

    Returns:
        Tuple of (transcription_text, srt_content, status_message)
    """
    if video_path is None:
        return "", "", "Please upload a video file."
    if model_choice not in MODELS:
        return "", "", "Please choose a valid model."

    with tempfile.TemporaryDirectory() as work_dir:
        audio_path = str(Path(work_dir) / "audio.wav")
        try:
            stream = ffmpeg.input(video_path)
            stream = ffmpeg.output(stream, audio_path, acodec="pcm_s16le", ac=1, ar="16k")
            ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
        except ffmpeg.Error as e:
            logger.error("FFmpeg error: %s", e.stderr.decode() if e.stderr else e)
            return "", "", "❌ Could not extract audio from this file. Check that it is a valid video."

        try:
            transcribe_options = {"fp16": False, "verbose": False}
            if language and language != "Auto-detect":
                transcribe_options["language"] = language
            result = get_model(model_choice).transcribe(audio_path, **transcribe_options)
        except Exception:
            logger.exception("Transcription failed")
            return "", "", "❌ Transcription failed. Please try again."

    text = result["text"].strip()
    segments = result.get("segments", [])
    detected_lang = result.get("language", "unknown")
    duration = segments[-1]["end"] if segments else 0
    status = (
        f"✅ Transcription complete! Language: {detected_lang.upper()}, "
        f"Duration: {int(duration // 60)}m {int(duration % 60)}s"
    )
    return text, generate_srt(segments), status


def save_download(content: str, suffix: str) -> Optional[str]:
    """Write content to a file for gr.File, after deleting downloads older than
    CACHE_MAX_AGE_SECONDS. Gradio serves its own cached copy, which delete_cache sweeps."""
    if not content:
        return None
    cutoff = time.time() - CACHE_MAX_AGE_SECONDS
    for old in DOWNLOAD_DIR.iterdir():
        if old.stat().st_mtime < cutoff:
            old.unlink(missing_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=suffix, dir=DOWNLOAD_DIR, delete=False, encoding="utf-8"
    ) as f:
        f.write(content)
        return f.name


# Gradio Interface
with gr.Blocks(
    title="EchoScribe - Video Transcription",
    delete_cache=(CACHE_SWEEP_SECONDS, CACHE_MAX_AGE_SECONDS),
) as demo:
    gr.Markdown(
        """
        # 🎬 EchoScribe
        ### Transform your videos into text using AI

        Upload a video and get accurate transcriptions powered by OpenAI Whisper.
        **No data is kept** - audio is deleted as soon as it is transcribed, and
        uploads and downloads are deleted within an hour.
        """
    )

    with gr.Row(), gr.Column(scale=1):
        video_input = gr.Video(label="Upload Video", include_audio=True)

        with gr.Row():
            model_dropdown = gr.Dropdown(
                choices=MODELS,
                value="base",
                label="Model Quality",
                info="base = balanced, large = best quality (slower)",
            )
            language_dropdown = gr.Dropdown(
                choices=LANGUAGES,
                value="Auto-detect",
                label="Language",
                info="Leave as Auto-detect for best results",
            )

        transcribe_btn = gr.Button("🎯 Transcribe Video", variant="primary", size="lg")

    status_output = gr.Markdown(label="Status")

    with gr.Tabs():
        with gr.TabItem("📝 Transcription"):
            text_output = gr.Textbox(
                label="Transcription Text (select all and copy)",
                lines=12,
                placeholder="Transcription will appear here...",
            )
            txt_download = gr.File(label="Download TXT")

        with gr.TabItem("🎬 Subtitles (SRT)"):
            srt_output = gr.Textbox(
                label="SRT Subtitles (select all and copy)",
                lines=12,
                placeholder="SRT subtitles will appear here...",
            )
            srt_download = gr.File(label="Download SRT")

    gr.Markdown(
        """
        ---
        **Tips:**
        - 🚀 Use **base** model for fast, accurate results
        - 🎯 Use **small** or **medium** for better accuracy
        - 🌍 Supports 99+ languages with auto-detection
        - 🔒 Privacy-focused: files are deleted within an hour

        *Powered by [OpenAI Whisper](https://github.com/openai/whisper)*
        """
    )

    def process_video(video, model_choice, language):
        text, srt, status = transcribe_video(video, model_choice, language)
        return text, srt, status, save_download(text, ".txt"), save_download(srt, ".srt")

    transcribe_btn.click(
        fn=process_video,
        inputs=[video_input, model_dropdown, language_dropdown],
        outputs=[text_output, srt_output, status_output, txt_download, srt_download],
    )


if __name__ == "__main__":
    demo.launch()
