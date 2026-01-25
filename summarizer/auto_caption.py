"""
Auto-caption video using Whisper via the transformers library (speech-to-text).
Returns plain text and SRT-formatted captions with timestamps.
Works with Python 3.8+ including 3.14; does not require the openai-whisper package.
"""
import os
import subprocess
import tempfile


def _get_ffmpeg_cmd():
    from .video_summarizer import _get_ffmpeg_cmd as _f
    return _f()


def _extract_audio_16k(video_path):
    """Extract 16 kHz mono WAV for Whisper. Returns (path to temp WAV or None, error_detail or None)."""
    ffmpeg = _get_ffmpeg_cmd()
    fd, wav = tempfile.mkstemp(suffix=".wav")
    os.close(fd)

    def _rm():
        try:
            os.remove(wav)
        except OSError:
            pass

    try:
        r = subprocess.run(
            [
                ffmpeg, "-y", "-i", video_path, "-vn",
                "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
                wav,
            ],
            capture_output=True,
            timeout=120,
            text=True,
        )
        if r.returncode == 0 and os.path.isfile(wav):
            return (wav, None)
        _rm()
        err = (r.stderr or r.stdout or "")[:400].strip() or ("ffmpeg exited %s" % r.returncode)
        return (None, err)
    except FileNotFoundError:
        _rm()
        return (None, "ffmpeg not found")
    except (subprocess.TimeoutExpired, OSError) as e:
        _rm()
        return (None, str(e)[:200])
    _rm()
    return (None, None)


def _format_srt_time(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    ms = int((sec % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _chunks_to_srt(chunks):
    """Build SRT from pipeline chunks: [{"timestamp": (s,e) or [s,e], "text": "..."}]."""
    srt = []
    for i, c in enumerate(chunks or [], 1):
        ts = c.get("timestamp")
        text = (c.get("text") or "").strip()
        if not text or ts is None:
            continue
        start, end = ts[0], ts[1]
        srt.append(f"{i}\n{_format_srt_time(start)} --> {_format_srt_time(end)}\n{text}\n")
    return "\n".join(srt) if srt else ""


_pipe = None


def _get_pipe():
    global _pipe
    if _pipe is None:
        from transformers import pipeline
        _pipe = pipeline(
            "automatic-speech-recognition",
            model="openai/whisper-base",
            return_timestamps=True,
        )
    return _pipe


def transcribe_video(video_path):
    """
    Transcribe video/audio and return text + SRT.
    Returns: {"text": str, "srt": str, "segments": list, "error": str|None}
    """
    wav, ext_err = _extract_audio_16k(video_path)
    if not wav:
        base = "Could not extract audio. "
        if ext_err == "ffmpeg not found":
            base += "FFmpeg not found. Download ffmpeg-release-essentials.zip from https://www.gyan.dev/ffmpeg/builds/ , extract, and put ffmpeg.exe in a folder. Then set that path in ffmpeg_path.txt or in FFMPEG_PATH / FFMPEG_BIN. See FFMPEG.md."
        else:
            base += "FFmpeg: %s" % (ext_err or "unknown error")
        return {"text": "", "srt": "", "segments": [], "error": base}

    try:
        import soundfile as sf

        data, sr = sf.read(wav, dtype="float32")
        if data.ndim > 1:
            data = data.mean(axis=1)
        pipe = _get_pipe()
        # Pass raw array so transformers doesn't call ffmpeg to load the file (avoids "ffmpeg was not found")
        out = pipe({"array": data, "sampling_rate": int(sr)})
    except Exception as e:
        return {"text": "", "srt": "", "segments": [], "error": str(e)}
    finally:
        try:
            os.remove(wav)
        except OSError:
            pass

    text = (out.get("text") or "").strip()
    chunks = out.get("chunks") or []
    srt = _chunks_to_srt(chunks)
    return {"text": text, "srt": srt, "segments": chunks, "error": None}
