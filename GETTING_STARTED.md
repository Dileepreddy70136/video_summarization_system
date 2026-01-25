# QUICK START - AUDIO EXTRACTION & AUTO CAPTIONS

## Your System is Ready! 🎉

Your video summarization system is fully configured with:
- ✓ Audio extraction (FFmpeg)
- ✓ Speech-to-text transcription (Whisper)
- ✓ Auto caption generation
- ✓ SRT subtitle export

---

## 🚀 Start Using It Now

### Step 1: Start the Web Server
Open a terminal and run:
```bash
cd c:\Users\DileepReddy\Downloads\video_summarization_system
python app.py
```

You should see:
```
* Running on http://127.0.0.1:5000
```

### Step 2: Open Your Browser
Click the link or go to: **http://localhost:5000**

### Step 3: Upload a Video with English Audio
1. Click the **"Video"** tab
2. **Drop your video** or click to select
3. **Check these options:**
   - ✓ Summarize video (optional - creates keyframe summary)
   - ✓ **Auto captions** (THIS EXTRACTS AUDIO & CONVERTS TO TEXT)
4. Click **"Process Video"**

### Step 4: Get Your Captions!
Wait for processing, then you'll see:
- **Caption Text**: Full transcription
- **Copy Button**: Copy all captions
- **Download SRT**: Save as subtitle file

---

## ⚙️ How Audio Extraction Works

### What Happens Behind the Scenes:

```
Your Video File
    ↓ (FFmpeg extracts audio)
Audio Stream (16 kHz mono WAV)
    ↓ (Whisper speech-to-text)
Transcribed Text
    ↓ (Formatted with timestamps)
Text Captions + SRT File
```

### Processing Times:
- 1 minute video → ~1 minute to process
- 5 minute video → ~5 minutes to process
- 10 minute video → ~10 minutes to process
- **First run may be slower** (downloads AI model ~140 MB)

---

## 📋 Output Formats

### 1. Plain Text Captions
```
Welcome to this video tutorial on how to use the video summarization system.
This system can automatically extract audio from videos and convert it to text.
The transcription appears in real-time as captions below.
```

### 2. SRT Subtitle File
```
1
00:00:00,000 --> 00:00:05,000
Welcome to this video tutorial on how to use
the video summarization system.

2
00:00:05,000 --> 00:00:10,000
This system can automatically extract audio
from videos and convert it to text.
```

---

## 🎯 Key Features

| Feature | What It Does |
|---------|-------------|
| **Audio Extract** | Pulls audio from any video format |
| **Speech-to-Text** | Converts audio to English text |
| **Timestamps** | Each caption shows exactly when spoken |
| **SRT Export** | Download subtitle file for video players |
| **Local Processing** | All done on your computer (no cloud) |
| **No API Keys** | No accounts, no subscriptions needed |

---

## 📁 File Organization

```
video_summarization_system/
├── app.py                    # Main Flask web server
├── requirements.txt          # Python dependencies
├── ffmpeg_path.txt          # FFmpeg location
├── AUTO_CAPTIONS_GUIDE.md   # Detailed guide
├── verify_system.py         # Verification script
├── templates/
│   └── index.html           # Web interface
├── static/
│   ├── script.js            # Frontend logic
│   └── style.css            # Styling
├── summarizer/
│   ├── auto_caption.py      # Audio extraction & transcription
│   ├── video_summarizer.py  # Video keyframe summary
│   └── youtube_summarizer.py # YouTube URL support
└── uploads/                 # Temporary video storage
```

---

## ⚠️ Troubleshooting

### "FFmpeg not found"
FFmpeg is configured at: `D:\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe`

If this path doesn't exist:
1. Download FFmpeg: https://www.gyan.dev/ffmpeg/builds/
2. Extract the ZIP
3. Edit `ffmpeg_path.txt` and add your FFmpeg path

### "Model downloading" (First Run Only)
- Whisper model (~140 MB) downloads automatically first time
- Requires internet connection for first run
- Subsequent runs use cached model (no download)

### Video Processing Takes Too Long
This is normal! 
- Video processing time = audio duration
- No way to speed this up (AI processes in real-time)
- Coffee break while it works!

### Captions Are Empty
1. Check if video has audio
2. Make sure audio is English
3. Verify audio is clear (not too quiet/loud/noisy)

---

## 💡 Pro Tips

1. **Best Results**: Clear audio without background noise
2. **Multiple Speakers**: Works with conversations (detects speaker changes)
3. **Music Videos**: Will transcribe lyrics but accuracy depends on music volume
4. **Background Noise**: Loud background = less accurate captions
5. **Format**: MP4 works best, but MP3, AVI, WebM, MKV all supported

---

## 🎬 Example Workflow

```
1. Record or find a video with English speech
   ↓
2. Open http://localhost:5000
   ↓
3. Upload video + check "Auto captions"
   ↓
4. Click "Process Video"
   ↓
5. Wait for processing (watch server output in terminal)
   ↓
6. See captions appear on the page
   ↓
7. Copy text or download SRT file
   ↓
8. Use captions in your video editor, player, etc.
```

---

## 📚 Use Cases

- **Video Tutorials**: Add captions for accessibility
- **Meeting Recordings**: Get meeting transcript
- **Language Learning**: Hear + read English
- **Video Editing**: Import SRT into editor
- **Accessibility**: Help deaf/hard-of-hearing viewers
- **Content Creation**: Repurpose video to social media text
- **Research**: Analyze what was said in videos

---

## 🔧 Advanced: Custom Models

The system uses **Whisper-base** (free, offline):
- Works for English and ~99 other languages
- Runs entirely on your computer
- No internet needed after first download
- Can be upgraded to larger models if needed

---

## 📞 System Status

Run this to verify everything is working:
```bash
python verify_system.py
```

Should show: ✓ All systems ready

---

## ✅ You're All Set!

Everything is installed and configured:
- ✓ Python 3.14.2
- ✓ Transformers library with Whisper
- ✓ FFmpeg for audio extraction
- ✓ Flask web server
- ✓ All dependencies

**Just run:** `python app.py`

**Then visit:** http://localhost:5000

**Upload a video and watch the magic happen!** 🎥✨

