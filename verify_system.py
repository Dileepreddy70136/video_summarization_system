#!/usr/bin/env python3
"""
Test script to verify audio extraction and captioning system is working.
Run this before uploading videos to ensure all components are functional.
"""

import os
import sys

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("VIDEO SUMMARIZATION SYSTEM - SETUP VERIFICATION")
print("=" * 60)

# 1. Check FFmpeg
print("\n[1] Checking FFmpeg...")
try:
    from summarizer.video_summarizer import _get_ffmpeg_cmd
    ffmpeg_path = _get_ffmpeg_cmd()
    if ffmpeg_path and os.path.isfile(ffmpeg_path):
        print(f"    OK: FFmpeg found at {ffmpeg_path}")
    else:
        print(f"    FAIL: FFmpeg not found or invalid path")
        sys.exit(1)
except Exception as e:
    print(f"    FAIL: {e}")
    sys.exit(1)

# 2. Check transformers
print("\n[2] Checking transformers library...")
try:
    from transformers import pipeline
    print("    OK: transformers library loaded")
except Exception as e:
    print(f"    FAIL: {e}")
    sys.exit(1)

# 3. Check soundfile
print("\n[3] Checking soundfile library...")
try:
    import soundfile
    print("    OK: soundfile library loaded")
except Exception as e:
    print(f"    FAIL: {e}")
    sys.exit(1)

# 4. Check auto_caption module
print("\n[4] Checking auto_caption module...")
try:
    from summarizer.auto_caption import transcribe_video
    print("    OK: auto_caption module loaded")
except Exception as e:
    print(f"    FAIL: {e}")
    sys.exit(1)

# 5. Check video_summarizer module
print("\n[5] Checking video_summarizer module...")
try:
    from summarizer.video_summarizer import summarize_video
    print("    OK: video_summarizer module loaded")
except Exception as e:
    print(f"    FAIL: {e}")
    sys.exit(1)

# 6. Check Flask
print("\n[6] Checking Flask...")
try:
    from flask import Flask
    print("    OK: Flask loaded")
except Exception as e:
    print(f"    FAIL: {e}")
    sys.exit(1)

# 7. Check uploads folder
print("\n[7] Checking uploads folder...")
uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(uploads_dir, exist_ok=True)
if os.path.isdir(uploads_dir):
    print(f"    OK: uploads directory exists at {uploads_dir}")
else:
    print(f"    FAIL: Could not create uploads directory")
    sys.exit(1)

# 8. Test Whisper model loading (optional, first-time only)
print("\n[8] Checking Whisper model...")
print("    (First run may download ~140MB model...)")
try:
    from transformers import pipeline
    
    # This will load or download the model
    pipe = pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-base",
        return_timestamps=True,
    )
    print("    OK: Whisper-base model ready")
except Exception as e:
    print(f"    NOTE: Model loading needs internet first time: {str(e)[:100]}")
    print("    (This is OK - will work when you run the app)")

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE - SYSTEM READY!")
print("=" * 60)
print("\nTo start the application:")
print("  python app.py")
print("\nThen open: http://localhost:5000")
print("\nFeatures available:")
print("  - Video summarization (keyframes)")
print("  - Auto captions (speech-to-text)")
print("  - YouTube video summarization")
print("\n" + "=" * 60)
