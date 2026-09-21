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

```bash
cd backend
python main.py
```

Then open **http://localhost:8000**

The UI and API are served from the same process.

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
# - App: http://localhost:8000
# - API docs: http://localhost:8000/docs
```

## 📍 Access Points

- **App**: `http://localhost:8000`
- **API documentation**: `http://localhost:8000/docs`
- **Health check**: `http://localhost:8000/health`

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

### Can't access the app

```bash
# Verify the server is running
curl http://localhost:8000/health

# Then open the UI
open http://localhost:8000
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

See [README.md](README.md) for complete documentation. For a free public demo, see [DEPLOY_FREE.md](DEPLOY_FREE.md).
