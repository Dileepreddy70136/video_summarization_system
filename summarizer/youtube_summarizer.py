"""
YouTube summarization: fetch transcript and summarize with BART.
Supports multiple languages and export formats (TXT, SRT).
"""
import re
from .text_summarizer import summarize_text

def _video_id_from_url(url):
    if not url or not isinstance(url, str):
        return None
    url = url.strip()
    # youtube.com/watch?v=ID
    m = re.search(r"(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
    if m:
        return m.group(1)
    # only 11-char id
    if re.fullmatch(r"[a-zA-Z0-9_-]{11}", url):
        return url
    return None

def get_available_languages(video_id):
    """
    Get list of available caption languages for a YouTube video.
    Returns: {"languages": [{"code": "en", "name": "English"}, ...], "error": str|None}
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        return {"languages": [], "error": "youtube-transcript-api not installed."}
    
    if not video_id:
        return {"languages": [], "error": "Invalid video ID."}
    
    try:
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Get manually created captions (usually most accurate)
        languages = []
        for transcript in transcripts:
            lang_name = transcript.language
            lang_code = transcript.language_code
            is_auto = transcript.is_generated
            label = f"{lang_name}" + (" (Auto)" if is_auto else "")
            languages.append({
                "code": lang_code,
                "name": lang_name,
                "label": label,
                "is_auto": is_auto
            })
        
        if not languages:
            return {"languages": [], "error": "No captions found for this video."}
        
        return {"languages": languages, "error": None}
    except Exception as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            error_msg = "Video not found."
        elif "forbidden" in error_msg.lower():
            error_msg = "Access denied - video may be private."
        return {"languages": [], "error": error_msg}

def format_as_srt(captions):
    """
    Convert captions to SRT format with timestamps.
    Format: index, start --> end, text
    """
    srt_lines = []
    for i, caption in enumerate(captions, 1):
        text = (caption.get("text") or "").strip()
        if not text:
            continue
        
        start_sec = caption.get("start", 0)
        duration = caption.get("duration", 0)
        end_sec = start_sec + duration
        
        # Convert seconds to SRT format HH:MM:SS,mmm
        def sec_to_srt(sec):
            h = int(sec // 3600)
            m = int((sec % 3600) // 60)
            s = int(sec % 60)
            ms = int((sec % 1) * 1000)
            return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
        
        srt_lines.append(f"{i}")
        srt_lines.append(f"{sec_to_srt(start_sec)} --> {sec_to_srt(end_sec)}")
        srt_lines.append(text)
        srt_lines.append("")
    
    return "\n".join(srt_lines)

def get_transcript_by_language(video_id, language_code):
    """
    Fetch transcript for a specific language.
    Returns: {"text": str, "captions": list, "srt": str, "error": str|None}
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        return {"text": "", "captions": [], "srt": "", "error": "youtube-transcript-api not installed."}
    
    if not video_id or not language_code:
        return {"text": "", "captions": [], "srt": "", "error": "Invalid video ID or language code."}
    
    try:
        captions = YouTubeTranscriptApi.get_transcript(video_id, languages=[language_code])
        
        if not captions:
            return {"text": "", "captions": [], "srt": "", "error": "No captions found for this language."}
        
        # Create plain text
        text = " ".join((c.get("text") or "").strip() for c in captions).strip()
        
        # Create SRT format
        srt = format_as_srt(captions)
        
        return {"text": text, "captions": captions, "srt": srt, "error": None}
    except Exception as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            error_msg = "Captions not available for this language."
        elif "forbidden" in error_msg.lower():
            error_msg = "Access denied."
        return {"text": "", "captions": [], "srt": "", "error": error_msg}

def summarize_youtube(url_or_video_id):
    """
    Get transcript from YouTube and return summarized text (English by default).
    Returns: {"summary": str, "transcript": str, "error": str|None}
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        return {"summary": "", "transcript": "", "error": "youtube-transcript-api not installed."}

    vid = _video_id_from_url(url_or_video_id)
    if not vid:
        return {"summary": "", "transcript": "", "error": "Invalid YouTube URL or video ID."}

    try:
        raw = YouTubeTranscriptApi.list_transcripts(vid).find_transcript(['en']).fetch()
        # raw: list of captions [{"text":"...","start":...}, ...]
        if not raw:
            return {"summary": "", "transcript": "", "error": "No captions available. This video might not have subtitles enabled."}
        
        transcript = " ".join((c.get("text") or "").strip() for c in raw).strip()
        if not transcript:
            return {"summary": "", "transcript": "", "error": "Transcript is empty. The video may not have captions."}

        summary = summarize_text(transcript)
        return {"summary": summary, "transcript": transcript, "error": None}
    except Exception as e:
        error_msg = str(e)
        # Provide helpful error messages for common issues
        if "no element found" in error_msg.lower() or "xml" in error_msg.lower():
            error_msg = "Could not fetch captions. The video may not have captions enabled or the URL may be invalid."
        elif "404" in error_msg or "not found" in error_msg.lower():
            error_msg = "Video not found. Check the YouTube URL is correct."
        elif "forbidden" in error_msg.lower():
            error_msg = "Access denied. The video may be private or age-restricted."
        elif "no transcripts" in error_msg.lower() or "transcript not found" in error_msg.lower():
            error_msg = "No captions available for this video. It may not have subtitles."
        
        return {"summary": "", "transcript": "", "error": error_msg}
