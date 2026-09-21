# 🎬 EchoScribe - Visual Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER BROWSER                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  frontend/index.html (Beautiful UI)                   │  │
│  │  - Drag & Drop Upload                                 │  │
│  │  - Model Selection (tiny/base/small/medium/large)     │  │
│  │  - Language Selection (optional)                      │  │
│  │  - Results Display                                    │  │
│  │  - Download Options (TXT/SRT/JSON)                    │  │
│  └───────────────────────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP POST /transcribe
                        │ (FormData with video file)
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                   FASTAPI BACKEND (Port 8000)                │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  backend/main.py                                      │  │
│  │  - Receives video upload                             │  │
│  │  - Validates file (size, format)                     │  │
│  │  - Saves to temp file                                │  │
│  └──────────────────────┬────────────────────────────────┘  │
│                         │                                    │
│                         ↓                                    │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  backend/utils.py                                     │  │
│  │  - Creates temporary file                            │  │
│  │  - Validates video format                            │  │
│  │  - Auto-cleanup on completion                        │  │
│  └──────────────────────┬────────────────────────────────┘  │
│                         │                                    │
│                         ↓                                    │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  backend/transcriber.py                               │  │
│  │  1. Extract Audio (FFmpeg)                           │  │
│  │     video.mp4 → audio.wav                            │  │
│  │  2. Load Whisper Model                               │  │
│  │     (cached after first load)                        │  │
│  │  3. Transcribe Audio                                 │  │
│  │     audio.wav → text + timestamps                    │  │
│  └──────────────────────┬────────────────────────────────┘  │
│                         │                                    │
│                         ↓                                    │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Return JSON Response:                                │  │
│  │  {                                                    │  │
│  │    "text": "Full transcription...",                  │  │
│  │    "language": "en",                                 │  │
│  │    "duration": 125.5,                                │  │
│  │    "segments": [{start, end, text}, ...],           │  │
│  │    "model_used": "base"                              │  │
│  │  }                                                    │  │
│  └──────────────────────┬────────────────────────────────┘  │
│                         │                                    │
│  [Temp files deleted]   │                                    │
└─────────────────────────┼────────────────────────────────────┘
                          │
                          ↓ JSON Response
┌─────────────────────────────────────────────────────────────┐
│                        USER BROWSER                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  frontend/app.js                                      │  │
│  │  - Displays transcription text                       │  │
│  │  - Shows metadata (language, duration)               │  │
│  │  - Renders timestamped segments                      │  │
│  │  - Enables downloads (TXT/SRT/JSON)                  │  │
│  │  - Copy to clipboard                                 │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

```
1. USER ACTION
   ├─→ Select/Drop Video File
   └─→ Click "Transcribe Video"
        ↓
2. FRONTEND VALIDATION
   ├─→ Check file type (.mp4, .avi, .mov, etc.)
   ├─→ Check file size (< 500MB)
   └─→ Show processing spinner
        ↓
3. API REQUEST
   └─→ POST /transcribe
       ├─ file: video.mp4
       ├─ model: "base"
       └─ language: "en" (optional)
            ↓
4. BACKEND PROCESSING
   ├─→ Save to temp file: /tmp/xyz123.mp4
   ├─→ Extract audio: /tmp/abc456.wav
   ├─→ Load Whisper model (cached)
   ├─→ Transcribe: audio → text
   └─→ Delete temp files
        ↓
5. RESPONSE
   └─→ JSON with text, segments, metadata
        ↓
6. FRONTEND DISPLAY
   ├─→ Show transcription
   ├─→ Display segments with timestamps
   └─→ Enable download buttons
        ↓
7. USER DOWNLOADS
   ├─→ TXT: Plain text file
   ├─→ SRT: Subtitle file
   └─→ JSON: Full data with timestamps
```

## File Structure

```
EchoScribe/
│
├─ 📱 FRONTEND (No frameworks, pure JS)
│  ├─ index.html      → UI structure
│  ├─ styles.css      → Beautiful design
│  └─ app.js          → Upload & download logic
│
├─ 🔧 BACKEND (Python FastAPI)
│  ├─ main.py         → API endpoints & routing
│  ├─ transcriber.py  → Whisper model integration
│  ├─ utils.py        → File handling & cleanup
│  └─ requirements.txt → Dependencies
│
├─ 🐳 DOCKER
│  ├─ Dockerfile      → Container image
│  ├─ docker-compose.yml → Easy deployment
│  └─ nginx.conf      → Production web server
│
├─ 🚀 AUTOMATION
│  ├─ setup.sh/bat    → One-time setup
│  └─ start.sh/bat    → Quick start
│
└─ 📚 DOCUMENTATION
   ├─ README.md       → Full docs
   ├─ QUICKSTART.md   → Fast setup
   └─ DEPLOY_FREE.md  → Optional Hugging Face hosting
```

## Quick Commands

```bash
# SETUP (First time only)
./setup.sh              # Linux/macOS
setup.bat               # Windows

# START
./start.sh              # Linux/macOS
start.bat               # Windows
# Open http://localhost:8000

# OR WITH DOCKER
docker-compose up --build

# CHECK STATUS
curl http://localhost:8000/health

# VIEW API DOCS
open http://localhost:8000/docs
```

## Technology Stack

```
┌─────────────────────────────────────────┐
│           FRONTEND                      │
│  HTML5 + CSS3 + Vanilla JavaScript      │
│  - No frameworks needed!                │
│  - Fast & lightweight                   │
│  - Modern ES6+ features                 │
└─────────────────────────────────────────┘
                   ↕
┌─────────────────────────────────────────┐
│           BACKEND                       │
│  Python 3.10+ + FastAPI                 │
│  - OpenAI Whisper (AI model)            │
│  - FFmpeg (audio extraction)            │
│  - Async file handling                  │
└─────────────────────────────────────────┘
                   ↕
┌─────────────────────────────────────────┐
│        INFRASTRUCTURE                   │
│  Docker + Docker Compose (optional)     │
│  - Easy deployment                      │
│  - Consistent environment               │
└─────────────────────────────────────────┘
```

## Whisper Models

```
┌─────────┬────────┬──────────┬───────────┐
│  Model  │  Size  │   RAM    │  Quality  │
├─────────┼────────┼──────────┼───────────┤
│  tiny   │  39MB  │   ~1GB   │    ★★     │
│  base   │  74MB  │   ~1GB   │   ★★★     │ ← Recommended
│  small  │ 244MB  │   ~2GB   │   ★★★★    │
│  medium │ 769MB  │   ~5GB   │  ★★★★★    │
│  large  │ 1550MB │  ~10GB   │  ★★★★★    │
└─────────┴────────┴──────────┴───────────┘
```

## Supported Formats

```
VIDEO FORMATS:
✅ MP4   ✅ AVI   ✅ MOV   ✅ MKV
✅ WebM  ✅ FLV   ✅ WMV   ✅ MPEG

EXPORT FORMATS:
📄 TXT  - Plain text transcription
🎬 SRT  - Subtitle file with timestamps
📊 JSON - Full data with segments

SIZE LIMIT: 500MB (configurable)
```

## Key Features Checklist

```
✅ Drag & drop upload
✅ Multiple video formats
✅ 5 quality models (tiny to large)
✅ 99+ language support
✅ Auto language detection
✅ Timestamped segments
✅ Copy to clipboard
✅ 3 export formats (TXT/SRT/JSON)
✅ No permanent storage
✅ Auto file cleanup
✅ Beautiful modern UI
✅ Responsive design
✅ Error handling
✅ Progress indicators
✅ Docker support
✅ Comprehensive docs
✅ Quick setup scripts
✅ API documentation
✅ Health checks
```

## What Happens to Your Files?

```
1. Upload    → Saved to temporary directory
2. Process   → Audio extracted to temp file
3. Transcribe → Model processes audio
4. Return    → Results sent to browser
5. DELETE    → All temp files removed immediately

⚡ IMPORTANT: No files are stored permanently!
🔒 Your privacy is protected by design.
```

## Getting Started in 3 Steps

```
1️⃣  SETUP
   ./setup.sh

2️⃣  START
   ./start.sh
   Open http://localhost:8000

3️⃣  USE
   Drop video → Transcribe → Download!
```

---

**That's it! You're ready to transcribe videos with EchoScribe!** 🎉
