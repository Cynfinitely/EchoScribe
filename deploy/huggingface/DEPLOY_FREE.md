# 🚀 Deploy EchoScribe for FREE

This guide shows you how to deploy EchoScribe so anyone on the internet can use it - **completely free**.

---

## Best Option: Hugging Face Spaces (Recommended)

**Why Hugging Face Spaces?**

- ✅ **Completely FREE** - no credit card needed
- ✅ **16GB RAM** on free CPU tier - enough for Whisper!
- ✅ **Designed for AI/ML** - perfect for Whisper models
- ✅ **Public URL** - anyone can access
- ✅ **Easy deployment** - just push to Git
- ✅ **Community** - thousands of similar apps

---

## Step-by-Step Deployment

### 1. Create a Hugging Face Account

1. Go to [huggingface.co](https://huggingface.co)
2. Click **Sign Up** (top right)
3. Create a free account

### 2. Create a New Space

1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. Fill in:
   - **Space name**: `echoscribe` (or any name you want)
   - **License**: MIT (or your preference)
   - **SDK**: Select **Gradio**
   - **Hardware**: **CPU basic** (free!)
   - **Visibility**: Public (so anyone can use it)
3. Click **Create Space**

### 3. Upload Your Files

**Option A: Via Web Interface (Easiest)**

1. In your new Space, click **Files** tab
2. Click **+ Add file** → **Upload files**
3. Upload these files from `deploy/huggingface/` in your EchoScribe folder:
   - `app.py` (the Gradio version of EchoScribe)
   - `requirements.txt`
4. Open the Space's `README.md` and set `sdk_version: 6.30.0` in its front matter, matching `gradio` in `requirements.txt`

**Option B: Via Git (Recommended)**

```bash
# Clone your Space (replace YOUR_USERNAME)
git clone https://huggingface.co/spaces/YOUR_USERNAME/echoscribe
cd echoscribe

# Copy the files
cp /path/to/EchoScribe/deploy/huggingface/app.py .
cp /path/to/EchoScribe/deploy/huggingface/requirements.txt .
# In README.md front matter, set: sdk_version: 6.30.0

# Push to Hugging Face
git add .
git commit -m "Add EchoScribe app"
git push
```

### 4. Wait for Build

- Hugging Face will automatically build your app
- First build takes 5-10 minutes (downloads Whisper model)
- You'll see a **Building** status, then **Running**

### 5. Share Your App!

Once running, your app is live at:

```
https://huggingface.co/spaces/YOUR_USERNAME/echoscribe
```

Share this URL with anyone - they can use it for free!

---

## Files Required for Hugging Face

Only 2 files needed:

### `app.py`

The Gradio-based UI, in `deploy/huggingface/app.py`. It is standalone and does not use `backend/`.

### `requirements.txt`

```
gradio==6.30.0
openai-whisper==20250625
ffmpeg-python==0.2.0
```

When you bump `gradio`, bump `sdk_version` in the Space's `README.md` to the same version.

---

## Configuration Options

### Change Default Model

Set the `WHISPER_MODEL` variable in the Space settings (see below), or change the fallback in `app.py`:

```python
_model_name = os.getenv("WHISPER_MODEL", "base")  # Change "base" to "small", "medium", etc.
```

### Use Secrets (Optional)

In your Space settings, you can add environment variables:

- `WHISPER_MODEL`: tiny, base, small, medium, or large

---

## Limitations of Free Tier

- **Cold starts**: App sleeps after inactivity, takes ~30s to wake
- **CPU only**: No GPU (transcription is slower but works fine)
- **Queue**: If many users, they wait in queue
- **Storage**: Limited temporary storage (fine for our use case)

### Upgrade Options (Still Cheap)

- **CPU Upgrade**: $0.03/hour - faster, no cold starts
- **GPU**: $0.60/hour - much faster transcription (T4 GPU)

---

## Alternative Free Options

### 1. Google Colab (Free but Manual)

Share a Colab notebook where users can run transcription:

```python
# In Google Colab
!pip install openai-whisper gradio
import whisper
import gradio as gr

model = whisper.load_model("base")

def transcribe(audio):
    result = model.transcribe(audio)
    return result["text"]

gr.Interface(fn=transcribe, inputs=gr.Audio(), outputs="text").launch()
```

**Pros**: Free GPU available
**Cons**: Users need Google account, manual setup

### 2. Streamlit Cloud (Free)

Similar to Hugging Face but less ML-focused:

- Create account at [streamlit.io](https://streamlit.io)
- Connect GitHub repo
- Deploy (may have RAM limitations)

### 3. Replit (Free Tier)

- Create account at [replit.com](https://replit.com)
- Import from GitHub
- Limited resources, may not work for larger models

---

## Quick Deployment Checklist

1. [ ] Create Hugging Face account
2. [ ] Create new Space (Gradio SDK, CPU basic)
3. [ ] Upload `app.py`
4. [ ] Upload `requirements.txt` and set `sdk_version: 6.30.0` in the Space README
5. [ ] Wait for build to complete
6. [ ] Test the app
7. [ ] Share the URL!

---

## Example Live Apps

See similar apps on Hugging Face:

- [openai/whisper](https://huggingface.co/spaces/openai/whisper) - Official demo
- Search "whisper transcription" on Hugging Face Spaces

---

## Troubleshooting

### Build Failed

- Check `requirements.txt` syntax
- Look at build logs for errors

### Out of Memory

- Use smaller model (tiny or base)
- Reduce max video length

### App Sleeping

- Normal on free tier
- Takes 30s to wake up
- Consider upgrade for always-on

### Slow Transcription

- Normal on CPU (free tier)
- 1 min video ≈ 1-3 min processing
- GPU upgrade makes it 10x faster

---

## Summary

**Fastest path to free deployment:**

1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. Create Space with Gradio SDK
3. Upload `app.py` and `requirements.txt`
4. Wait 5-10 minutes
5. Share your URL! 🎉

Your app will be live at:
`https://huggingface.co/spaces/YOUR_USERNAME/echoscribe`

---

**That's it! You now have a free, public video transcription service!** 🚀
