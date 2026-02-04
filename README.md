# 🎬 EchoScribe

**Transform your videos into text using AI**

EchoScribe is a web-based video transcription tool powered by OpenAI's open-source Whisper model. Upload a video, and get accurate transcriptions with timestamps—all processed locally with no permanent storage.

## ✨ Features

- 🎥 **Multi-format Support**: Works with MP4, AVI, MOV, MKV, WebM, and more
- 🤖 **Powered by Whisper**: Uses OpenAI's state-of-the-art speech recognition
- 🌍 **Multi-language**: Supports 99+ languages with automatic detection
- ⚡ **Multiple Model Options**: Choose speed vs accuracy based on your needs
- 📝 **Multiple Export Formats**: Download as TXT, SRT (subtitles), or JSON
- 🔒 **Privacy-Focused**: No permanent storage—files are deleted immediately after processing
- 🎨 **Modern UI**: Beautiful, responsive interface with drag-and-drop
- 🐳 **Docker Ready**: Easy deployment with Docker support

## 📋 Requirements

### Local Development

- Python 3.10 or higher
- FFmpeg
- 1-10GB RAM (depending on model choice)

### Docker

- Docker
- Docker Compose

## 🚀 Quick Start

### Option 1: Local Development

1. **Install FFmpeg**

   macOS:

   ```bash
   brew install ffmpeg
   ```

   Ubuntu/Debian:

   ```bash
   sudo apt update
   sudo apt install ffmpeg
   ```

   Windows:
   Download from [ffmpeg.org](https://ffmpeg.org/download.html)

2. **Clone and Setup**

   ```bash
   cd EchoScribe
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r backend/requirements.txt
   ```

3. **Run the Backend**

   ```bash
   cd backend
   python main.py
   ```

   The API will be available at `http://localhost:8000`

4. **Open the Frontend**

   Simply open `frontend/index.html` in your browser, or serve it with a simple HTTP server:

   ```bash
   # Python 3
   python -m http.server 3000 --directory frontend
   ```

   Then visit `http://localhost:3000`

### Option 2: Docker

1. **Build and Run**

   ```bash
   docker-compose up --build
   ```

2. **Access the Application**
   - Backend API: `http://localhost:8000`
   - Frontend: Open `frontend/index.html` in your browser
   - API Docs: `http://localhost:8000/docs`

## 🎯 Usage

1. **Upload Video**: Drag and drop or click to select a video file (max 500MB)
2. **Choose Model**: Select from tiny, base, small, medium, or large
3. **Select Language** (Optional): Choose language or let Whisper auto-detect
4. **Transcribe**: Click the transcribe button and wait for processing
5. **Download**: Get your transcription as TXT, SRT, or JSON

## 🔧 Configuration

### Model Selection

Choose based on your needs:

| Model  | Speed      | Accuracy   | RAM Usage | Best For        |
| ------ | ---------- | ---------- | --------- | --------------- |
| tiny   | ⚡⚡⚡⚡⚡ | ⭐⭐       | ~1GB      | Quick drafts    |
| base   | ⚡⚡⚡⚡   | ⭐⭐⭐     | ~1GB      | **Recommended** |
| small  | ⚡⚡⚡     | ⭐⭐⭐⭐   | ~2GB      | Better accuracy |
| medium | ⚡⚡       | ⭐⭐⭐⭐⭐ | ~5GB      | High accuracy   |
| large  | ⚡         | ⭐⭐⭐⭐⭐ | ~10GB     | Best accuracy   |

### Environment Variables

Create a `.env` file in the project root:

```env
WHISPER_MODEL=base    # Default model (tiny, base, small, medium, large)
PORT=8000             # Backend port
```

### File Size Limits

Default maximum file size is 500MB. To change this, edit `backend/utils.py`:

```python
MAX_FILE_SIZE = 500 * 1024 * 1024  # Change this value
```

## 📡 API Endpoints

### `POST /transcribe`

Transcribe a video file.

**Request:**

- `file`: Video file (multipart/form-data)
- `model`: Model name (optional, default: base)
- `language`: Language code (optional)

**Response:**

```json
{
  "text": "Full transcription text...",
  "language": "en",
  "duration": 125.5,
  "segments": [
    {
      "start": 0.0,
      "end": 3.5,
      "text": "Hello world"
    }
  ],
  "model_used": "base"
}
```

### `POST /transcribe/srt`

Transcribe and return SRT subtitle format.

### `GET /models`

List available Whisper models.

### `GET /health`

Health check endpoint.

## 🏗️ Project Structure

```
EchoScribe/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── transcriber.py       # Whisper integration
│   ├── utils.py             # Utilities and file handling
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── index.html           # Main UI
│   ├── styles.css           # Styling
│   └── app.js               # Frontend logic
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose setup
├── nginx.conf               # Optional Nginx config
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 🐛 Troubleshooting

### "Failed to extract audio from video"

- Ensure FFmpeg is installed: `ffmpeg -version`
- Check video file is not corrupted
- Try a different video format

### "Model loading failed"

- Check internet connection (first run downloads model)
- Ensure sufficient disk space (~1-10GB per model)
- Models are cached in `~/.cache/whisper/`

### Backend not connecting

- Verify backend is running: `curl http://localhost:8000/health`
- Check firewall settings
- Ensure port 8000 is not in use

### Out of memory errors

- Use a smaller model (tiny or base)
- Close other applications
- Try shorter videos
- Increase system swap/virtual memory

## 🚀 Deployment

### Production Deployment Tips

1. **Use Environment Variables** for configuration
2. **Set up Nginx** as reverse proxy (see `nginx.conf`)
3. **Enable HTTPS** with Let's Encrypt
4. **Set CORS origins** to specific domains in `backend/main.py`
5. **Add rate limiting** for API endpoints
6. **Monitor resource usage** (RAM, CPU, disk space)
7. **Consider GPU acceleration** for faster processing

### Cloud Deployment

**Docker-based platforms** (easiest):

- Heroku
- Google Cloud Run
- AWS ECS
- DigitalOcean App Platform

**Note**: Whisper models download on first use (~40MB - 1.5GB). Build time may be long.

## 🤝 Contributing

Contributions are welcome! Feel free to:

- Report bugs
- Suggest features
- Submit pull requests

## 📄 License

This project uses OpenAI's Whisper model, which is released under the MIT License.

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - The amazing speech recognition model
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [FFmpeg](https://ffmpeg.org/) - Multimedia processing

## ⚠️ Limitations

- Processing time depends on video length and model size
- Large models require significant RAM
- First run downloads model weights (may take time)
- No GPU acceleration by default (CPU only)

## 📞 Support

For issues and questions:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review [Whisper documentation](https://github.com/openai/whisper)
3. Open an issue in this repository

---

**Made with ❤️ using OpenAI Whisper**
