# Audio Extraction & Auto Captions Guide

## How It Works

Your video summarization system includes automatic audio extraction and speech-to-text caption generation.

### 1. **Audio Extraction** (`summarizer/auto_caption.py`)
When you upload a video with "Auto captions" enabled:
- **Extracts audio** from the video using FFmpeg
- **Converts to 16 kHz mono WAV** (required for Whisper speech recognition)
- **Handles various video formats**: MP4, AVI, MOV, WebM, etc.

### 2. **Speech-to-Text Transcription**
- Uses **OpenAI Whisper Base model** via `transformers` library
- Converts audio to text automatically
- **Returns two formats:**
  - **Plain text**: Full transcription as readable text
  - **SRT format**: Subtitle format with timestamps (start → end times)

### 3. **Display on Webpage**
Captions are displayed in the "Auto Captions" section below:
- **Caption text box**: Shows the full transcription
- **Copy button**: Copy all captions to clipboard
- **Download SRT button**: Download subtitle file for video players

---

## Quick Start

### 1. Ensure FFmpeg is Set Up
FFmpeg must be installed and configured:
- **Check**: `ffmpeg_path.txt` has a valid path to `ffmpeg.exe`
- **Current path**: `D:\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe`
- **If missing**: Download from https://www.gyan.dev/ffmpeg/builds/

### 2. Run the Web Application
```bash
cd c:\Users\DileepReddy\Downloads\video_summarization_system
python app.py
```

Then open: **http://localhost:5000**

### 3. Upload a Video
1. Click **"Video" tab** (or upload on the page)
2. **Drop your video** or click to select a file
3. **Check "Auto captions (speech-to-text)"** checkbox
4. Click **"Process Video"**
5. Wait for processing (depends on video length)
6. **Captions appear** in the "Auto Captions" section

---

## Features

| Feature | Details |
|---------|---------|
| **Input Formats** | MP4, AVI, MOV, WebM, FLV, MKV, etc. |
| **Audio Quality** | Converts to 16 kHz mono (optimal for Whisper) |
| **Language** | English (built-in with Whisper-base) |
| **Output Formats** | Plain text + SRT subtitles |
| **Processing** | Runs locally on your computer |
| **No API Key** | Uses free local Whisper model |

---

## Troubleshooting

### Issue: "FFmpeg not found"
**Solution**: 
1. Download FFmpeg essentials from https://www.gyan.dev/ffmpeg/builds/
2. Extract the ZIP file
3. Add the path to `ffmpeg_path.txt` (one path per line)
4. Example:
   ```
   D:\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe
   C:\Users\YourName\Downloads\ffmpeg\bin
   ```

### Issue: "Could not extract audio"
**Solution**: 
1. Ensure video file is not corrupted
2. Try a different video format (MP4 works best)
3. Check that FFmpeg works: `ffmpeg -version` in terminal

### Issue: Captions are empty or wrong
**Solution**:
1. Ensure video has clear audio/speech
2. Check internet connection (model downloads on first use)
3. Whisper-base works best with English speech
4. Loud background noise may reduce accuracy

### Issue: Long videos take too long
**Solution**:
- Whisper processes in real-time audio length
- 1-minute video ≈ 1 minute processing
- 10-minute video ≈ 10 minutes processing (first time may be longer)
- Model loads from cache after first use

---

## System Requirements

### Installed Packages
- `transformers` - Whisper model & speech recognition
- `torch` - Deep learning framework for Whisper
- `soundfile` - Audio file reading
- `ffmpeg` - Video/audio processing (external)

### Python Version
- Python 3.8+ (you have 3.14.2)
- Virtual environment configured and active

### Disk Space
- Whisper model cache: ~140 MB (downloads on first use)
- Typically goes to: `~/.cache/huggingface/hub/`

---

## How to Use Captions

### Option 1: Copy & Paste
1. Click **"Copy text"** button
2. Paste into Word, Notepad, or any editor

### Option 2: Download SRT File
1. Click **"Download SRT"** button
2. Open in any video player (VLC, Windows Media Player, etc.)
3. Video player automatically displays captions

### Option 3: Use Captions File
- SRT format is compatible with:
  - Video editing software (Adobe Premiere, DaVinci Resolve, OBS)
  - Online subtitle services
  - Most video players

---

## Tips for Best Results

1. **Clear audio**: Use videos with clear speech
2. **Minimal background noise**: Reduce ambient noise for better accuracy
3. **English speech**: Whisper-base is optimized for English
4. **Video quality**: No minimum video quality required (audio matters)
5. **File format**: MP4 format most compatible

---

## Next Steps

- ✓ System is ready to use
- ✓ All dependencies installed
- ✓ FFmpeg configured
- Start the Flask app and upload your first video!

For questions or issues, check the server output in the terminal for detailed error messages.
