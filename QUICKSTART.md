# 🚀 Quick Start Guide

## 1️⃣ First Time Setup (5 minutes)

### Prerequisites

- Python 3.10+ installed
- FFmpeg installed

### Setup Steps

**Linux/macOS:**

```bash
./setup.sh
```

**Windows:**

```cmd
setup.bat
```

Or manually:

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r backend/requirements.txt
```

## 2️⃣ Running the Application

### Method 1: Using Start Scripts

**Linux/macOS:**

```bash
./start.sh
```

**Windows:**

```cmd
start.bat
```

### Method 2: Manual Start

**Terminal 1 - Backend:**

```bash
cd backend
python main.py
```

**Terminal 2 - Frontend (optional):**

```bash
python -m http.server 3000 --directory frontend
```

Then:

- Open `frontend/index.html` in your browser
- OR visit `http://localhost:3000` if using http.server

## 3️⃣ Using EchoScribe

1. **Upload Video** 📹

   - Drag & drop or click to browse
   - Supports: MP4, AVI, MOV, MKV, WebM (max 500MB)

2. **Choose Model** 🎯

   - **Tiny**: Super fast, less accurate
   - **Base**: ✅ Recommended balance
   - **Small**: Better accuracy
   - **Medium/Large**: Best quality, slower

3. **Select Language** 🌍 (optional)

   - Leave blank for auto-detection
   - Or choose from 99+ languages

4. **Click Transcribe** ⚡

   - Wait for processing (depends on video length)
   - First run downloads model (~74MB for base)

5. **Download Results** 📥
   - **TXT**: Plain text transcription
   - **SRT**: Subtitle file with timestamps
   - **JSON**: Full data with segments

## 4️⃣ Docker Quick Start

```bash
# Build and run
docker-compose up --build

# Access
# - Backend: http://localhost:8000
# - Frontend: Open frontend/index.html
# - API Docs: http://localhost:8000/docs
```

## 📍 Access Points

- **Frontend**: `frontend/index.html` or `http://localhost:3000`
- **Backend API**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`

## ⚡ Common Commands

```bash
# Check if backend is running
curl http://localhost:8000/health

# List available models
curl http://localhost:8000/models

# View API documentation
open http://localhost:8000/docs  # macOS
start http://localhost:8000/docs # Windows
```

## 🐛 Quick Troubleshooting

### Backend won't start

```bash
# Check Python
python3 --version  # Should be 3.10+

# Check FFmpeg
ffmpeg -version

# Reinstall dependencies
pip install -r backend/requirements.txt
```

### Can't access frontend

```bash
# Make sure you're opening the right file
open frontend/index.html

# Or use a web server
python -m http.server 3000 --directory frontend
```

### Transcription fails

- Check video file is valid (not corrupted)
- Try a smaller model (tiny or base)
- Check available RAM
- View logs in terminal for errors

## 💡 Tips

- **First transcription takes longer** (downloads model)
- **Use 'base' model** for best speed/accuracy balance
- **Close other apps** if you get memory errors
- **GPU not required** but speeds up processing
- **Files are temporary** - deleted after processing

## 🔗 More Information

See [README.md](README.md) for complete documentation.
