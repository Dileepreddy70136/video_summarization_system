import os
import shutil
import subprocess
import tempfile

import cv2


def _get_ffmpeg_cmd():
    """Resolve ffmpeg executable: FFMPEG_PATH, FFMPEG_BIN, PATH, or common locations."""
    # 1. Explicit env: full path to ffmpeg.exe (or ffmpeg on Unix)
    for key in ("FFMPEG_PATH", "FFMPEG"):
        exe = os.environ.get(key)
        if exe and exe.strip() and os.path.isfile(exe.strip()):
            return exe.strip()
    # 2. FFMPEG_BIN = directory containing ffmpeg
    bin_dir = os.environ.get("FFMPEG_BIN")
    if bin_dir and os.path.isdir(bin_dir):
        name = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
        candidate = os.path.join(bin_dir, name)
        if os.path.isfile(candidate):
            return candidate
    # 2.5. Project ffmpeg_path.txt (full path to ffmpeg.exe, or folder containing it)
    _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _txt = os.path.join(_root, "ffmpeg_path.txt")
    if os.path.isfile(_txt):
        try:
            with open(_txt, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.split("#")[0].strip()
                    if not line:
                        continue
                    P = os.path.expandvars(os.path.expanduser(line))
                    if os.path.isfile(P):
                        return P
                    if os.path.isdir(P):
                        c = os.path.join(P, "ffmpeg.exe" if os.name == "nt" else "ffmpeg")
                        if os.path.isfile(c):
                            return c
        except OSError:
            pass
    # 3. In system PATH
    w = shutil.which("ffmpeg")
    if w:
        return w
    # 4. Common Windows locations
    if os.name == "nt":
        # 4a. Explicit D:\ (or similar) essentials build
        for abs_path in ("D:\\ffmpeg-8.0.1-essentials_build\\bin\\ffmpeg.exe",):
            if os.path.isfile(abs_path):
                return abs_path
        d = os.path.expanduser("~/Downloads")
        for folder in (
            "ffmpeg-8.0.1",
            "ffmpeg-8.0.1/ffmpeg-8.0.1",
            "ffmpeg-8.0.1-full_build",
            "ffmpeg-8.0.1-essentials_build",
        ):
            exe = os.path.join(d, folder.replace("/", os.sep), "bin", "ffmpeg.exe")
            if os.path.isfile(exe):
                return exe
        # 4.5. Any ffmpeg* folder in Downloads with bin/ffmpeg.exe
        try:
            if os.path.isdir(d):
                for name in os.listdir(d):
                    if name.lower().startswith("ffmpeg"):
                        exe = os.path.join(d, name, "bin", "ffmpeg.exe")
                        if os.path.isfile(exe):
                            return exe
        except OSError:
            pass
    # 5. imageio-ffmpeg bundled binary (pip install imageio-ffmpeg) – optional, not in requirements
    try:
        from imageio_ffmpeg import get_ffmpeg_exe  # pyright: ignore[reportMissingImports]
        exe = get_ffmpeg_exe()
        if exe and isinstance(exe, str) and exe.strip():
            return exe.strip()
    except Exception:
        pass
    return "ffmpeg"


def _reencode_h264_for_web(path):
    """Re-encode to H.264 with faststart so it plays in Chrome, Edge, Firefox."""
    ffmpeg = _get_ffmpeg_cmd()
    try:
        fd, tmp = tempfile.mkstemp(suffix=".mp4", dir=os.path.dirname(path))
        os.close(fd)
        r = subprocess.run(
            [
                ffmpeg, "-y", "-i", path,
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-movflags", "+faststart",
                "-an",  # drop audio to avoid codec issues
                tmp,
            ],
            capture_output=True,
            timeout=300,
        )
        if r.returncode == 0 and os.path.isfile(tmp):
            os.replace(tmp, path)
        else:
            try:
                os.remove(tmp)
            except OSError:
                pass
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        try:
            os.remove(tmp)
        except (NameError, OSError):
            pass


def summarize_video(input_path, output_path):
    """Summarize video by extracting key frames. Returns summary text or raises exception."""
    
    # Validate input file exists
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input video not found: {input_path}")
    
    # Check file size
    file_size = os.path.getsize(input_path)
    if file_size < 1024:
        raise ValueError(f"Input video file too small ({file_size} bytes), likely corrupted")
    
    cap = cv2.VideoCapture(input_path)
    
    # Validate video can be opened
    if not cap.isOpened():
        cap.release()
        raise ValueError(f"Cannot open video file: {input_path}. File may be corrupted.")

    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 24
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Validate video properties
    if width <= 0 or height <= 0:
        cap.release()
        raise ValueError(f"Invalid video dimensions: {width}x{height}")
    
    if total_frames <= 0:
        cap.release()
        raise ValueError(f"Video has no frames or is corrupted (frame_count={total_frames})")
    
    # Calculate original duration
    original_duration = total_frames / fps if fps > 0 else 0

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    if not out.isOpened():
        cap.release()
        out.release()
        raise ValueError(f"Cannot create output video: {output_path}")

    frame_count = 0
    saved_frames = 0
    read_errors = 0
    max_read_errors = 10  # Allow some errors but not too many

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            read_errors += 1
            if read_errors > max_read_errors:
                print(f"[WARNING] Too many read errors ({read_errors}), stopping at frame {frame_count}")
                break
            if frame_count >= total_frames:
                # Natural end of video
                break
            continue

        # every 30th frame = key frame
        if frame_count % 30 == 0:
            out.write(frame)
            saved_frames += 1

        frame_count += 1

    cap.release()
    out.release()
    
    # Validate output was created
    if not os.path.exists(output_path) or os.path.getsize(output_path) < 1024:
        raise ValueError(f"Failed to create valid output video: {output_path}")
    
    # Calculate summarized duration
    summarized_duration = saved_frames / fps if fps > 0 else 0
    reduction_percentage = ((original_duration - summarized_duration) / original_duration * 100) if original_duration > 0 else 0

    # Re-encode to H.264 so the file plays in browsers (mp4v often fails in Chrome/Edge/Firefox)
    _reencode_h264_for_web(output_path)

    # Format durations
    def format_duration(seconds):
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        if mins > 0:
            return f"{mins}m {secs}s"
        return f"{secs}s"

    # 🔥 PROFESSIONAL CAPTION-STYLE SUMMARY
    summary_text = f"""
📌 Video Summary Statistics:

• Original Duration: {format_duration(original_duration)} ({total_frames} frames)
• Summary Duration: {format_duration(summarized_duration)} ({saved_frames} keyframes)
• Reduction: {reduction_percentage:.1f}% shorter

🧠 Technique Used:
Key-frame extraction every 30 frames to preserve important visual moments while reducing video length.

✓ The summarized video maintains visual continuity while being significantly shorter.
"""

    return summary_text.strip()
