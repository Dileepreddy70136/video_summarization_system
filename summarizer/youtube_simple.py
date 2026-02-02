"""
Simple YouTube video summarization using transcript.
No AI models, just extractive summarization.
"""
import re
import sys
import os


def download_youtube_audio(url, output_dir):
    """Download audio from YouTube video for Whisper transcription - uses unique filenames"""
    try:
        import yt_dlp
        import uuid
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Use UUID for unique filename to prevent file locking issues
        unique_id = str(uuid.uuid4())
        output_template = os.path.join(output_dir, f"{unique_id}.%(ext)s")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        
        print(f"[AUDIO] Downloading audio for Whisper transcription...")
        sys.stdout.flush()
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            audio_path = os.path.join(output_dir, f"{unique_id}.mp3")
        
        if os.path.exists(audio_path):
            print(f"[AUDIO] ✓ Audio downloaded: {audio_path}")
            sys.stdout.flush()
            return audio_path
        
        print("[AUDIO] Audio file not found after download")
        sys.stdout.flush()
        return None
        
    except Exception as e:
        print(f"[ERROR] Audio download failed: {e}")
        sys.stdout.flush()
        return None


def clean_telugu_text(text):
    """Clean text to keep only Telugu characters, basic punctuation, and spaces.
    Removes junk unicode and mixed-language garbage."""
    import re
    
    if not text:
        return ""
    
    # Telugu Unicode range: 0C00-0C7F
    # Keep: Telugu chars, spaces, basic punctuation, numbers
    # Remove: everything else (junk unicode, mixed language garbage)
    cleaned = re.sub(
        r'[^\u0C00-\u0C7F\s.,!?;:()\[\]"\'-0-9]+',  # Keep only Telugu + basic punctuation + numbers
        '',  # Remove everything else
        text
    )
    
    # Remove excessive whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned


def clean_english_text(text):
    """Clean English text to remove junk unicode while preserving English and basic punctuation."""
    import re
    
    if not text:
        return ""
    
    # Keep: English letters (a-z, A-Z), numbers, spaces, basic punctuation
    # Remove: junk unicode and special characters
    cleaned = re.sub(
        r'[^a-zA-Z0-9\s.,!?;:()\[\]"\'-]+',
        '',
        text
    )
    
    # Remove excessive whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned


def count_telugu_characters(text):
    """Count Telugu Unicode characters in text.
    
    WHY: We need to detect if there's actual Telugu speech vs. hallucinated
    Urdu/Arabic/Tamil when Whisper processes music-only videos.
    
    Returns: Number of Telugu characters (0C00-0C7F range)
    """
    import re
    if not text:
        return 0
    # Count only Telugu Unicode characters
    telugu_chars = re.findall(r'[\u0C00-\u0C7F]', text)
    return len(telugu_chars)


def validate_telugu_speech(text, min_total_chars=40, min_telugu_chars=20):
    """Validate if text contains meaningful Telugu speech.
    
    WHY: Music-only/WhatsApp status videos often result in:
    - Very short transcriptions (< 40 chars)
    - Hallucinated non-Telugu text (Urdu, Arabic, Tamil)
    - We must reject these and show a proper Telugu message
    
    Args:
        text: Transcribed text to validate
        min_total_chars: Minimum total characters (default: 40)
        min_telugu_chars: Minimum Telugu characters (default: 20)
    
    Returns:
        dict with 'valid' (bool) and 'reason' (str in Telugu)
    """
    if not text or len(text.strip()) == 0:
        return {
            'valid': False,
            'reason': 'ఈ వీడియోలో స్పీచ్ గుర్తించబడలేదు. దయచేసి మరొక వీడియోను ప్రయత్నించండి.'
        }
    
    total_chars = len(text.strip())
    telugu_chars = count_telugu_characters(text)
    
    # Check 1: Too short - likely music only or very brief audio
    if total_chars < min_total_chars:
        return {
            'valid': False,
            'reason': f'ఈ వీడియోలో తగినంత స్పీచ్ లేదు ({total_chars} అక్షరాలు). సంగీతం మాత్రమే ఉన్న వీడియోలకు సారాంశం సృష్టించలేము.'
        }
    
    # Check 2: Not enough Telugu - likely hallucinated in wrong language
    if telugu_chars < min_telugu_chars:
        return {
            'valid': False,
            'reason': f'ఈ వీడియోలో తెలుగు స్పీచ్ కనుగొనబడలేదు ({telugu_chars} తెలుగు అక్షరాలు). దయచేసి తెలుగు వీడియోను ఎంచుకోండి.'
        }
    
    # Valid Telugu speech detected
    return {
        'valid': True,
        'reason': ''
    }


def whisper_transcribe(audio_path, language='english'):
    """Transcribe audio using Whisper with speech validation.
    
    FIX 1: Use user-selected language for transcription
    FIX 2: Disable fp16=False for CPU compatibility
    FIX 3: Add no_speech_threshold to detect music-only videos
    FIX 4: Validate Telugu speech to prevent hallucinations
    FIX 5: Clean output to remove junk unicode based on language
    
    Args:
        audio_path: Path to audio file
        language: 'english' or 'telugu' (from form selection)
    
    Returns:
        dict with 'success', 'text', 'error', 'is_music_only' keys
    """
    try:
        import whisper
        
        # Convert language names to Whisper codes
        lang_map = {
            'telugu': 'te',
            'english': 'en'
        }
        whisper_lang = lang_map.get(language.lower(), 'en')  # Default to English if unknown
        lang_display = language.upper()
        
        print(f"[WHISPER] Loading Whisper model...")
        sys.stdout.flush()
        model = whisper.load_model("base")  # You can use "small", "medium", "large" for better accuracy
        
        print(f"[WHISPER] Transcribing audio in {lang_display} with speech detection...")
        sys.stdout.flush()
        
        # FIX 1, 2, 3: Use selected language, disable FP16, enable speech detection
        # WHY no_speech_threshold: Detects music-only videos and prevents hallucinations
        result = model.transcribe(
            audio_path,
            language=whisper_lang,    # FORCE selected language
            fp16=False,               # CPU compatibility
            no_speech_threshold=0.6   # Detect music-only (higher = stricter)
        )
        
        # Get raw transcription
        raw_transcript = result["text"]
        print(f"[WHISPER] Raw transcription length: {len(raw_transcript)} chars")
        sys.stdout.flush()
        
        # FIX 4: VALIDATE TELUGU SPEECH before proceeding
        # WHY: Prevents hallucinated Urdu/Arabic/Tamil summaries when Telugu is selected
        if language.lower() == 'telugu':
            validation = validate_telugu_speech(raw_transcript)
            if not validation['valid']:
                print(f"[WHISPER] ⚠ Telugu speech validation failed: {validation['reason']}")
                print(f"[WHISPER] 🔄 Auto-switching to ENGLISH transcription...")
                sys.stdout.flush()
                
                # AUTO-FALLBACK: Retry with English instead of failing
                try:
                    result_en = model.transcribe(
                        audio_path,
                        language='en',    # Switch to English
                        fp16=False,
                        no_speech_threshold=0.6
                    )
                    raw_transcript = result_en["text"]
                    print(f"[WHISPER] ✓ Auto-switched to English transcription ({len(raw_transcript)} chars)")
                    sys.stdout.flush()
                    
                    # Update language to English for rest of processing
                    language = 'english'
                    whisper_lang = 'en'
                    lang_display = 'ENGLISH'
                except Exception as retry_error:
                    print(f"[WHISPER] ✗ English fallback also failed: {retry_error}")
                    sys.stdout.flush()
                    return {
                        'success': False,
                        'text': '',
                        'error': 'ఈ వీడియోలో స్పీచ్ గుర్తించబడలేదు. (Speech not detected)',
                        'is_music_only': True
                    }
            else:
                print(f"[WHISPER] ✓ Telugu speech validated ({count_telugu_characters(raw_transcript)} Telugu chars)")
                sys.stdout.flush()
        
        # FIX 5: Clean the transcript based on language
        if language.lower() == 'telugu':
            cleaned_transcript = clean_telugu_text(raw_transcript)
            # If Telugu cleaning removed everything, it's not really Telugu
            if not cleaned_transcript or len(cleaned_transcript.strip()) == 0:
                print("[WHISPER] ✗ Telugu cleaning removed all text - not Telugu speech")
                sys.stdout.flush()
                return {
                    'success': False,
                    'text': '',
                    'error': 'ఈ వీడియోలో తెలుగు స్పీచ్ కనుగొనబడలేదు. దయచేసి తెలుగు వీడియోను ఎంచుకోండి.',
                    'is_music_only': True
                }
        else:
            cleaned_transcript = clean_english_text(raw_transcript)
        
        # Final check: ensure we have meaningful content
        if not cleaned_transcript or len(cleaned_transcript.strip()) < 10:
            error_msg = 'ఈ వీడియోలో స్పీచ్ గుర్తించబడలేదు.' if language.lower() == 'telugu' else 'No speech detected in this video.'
            print(f"[WHISPER] ✗ Insufficient cleaned text ({len(cleaned_transcript)} chars)")
            sys.stdout.flush()
            return {
                'success': False,
                'text': '',
                'error': error_msg,
                'is_music_only': True
            }
        
        print(f"[WHISPER] Cleaned transcription length: {len(cleaned_transcript)} chars")
        print(f"[WHISPER] ✓ {lang_display} transcription complete")
        sys.stdout.flush()
        
        return {
            'success': True,
            'text': cleaned_transcript,
            'error': '',
            'is_music_only': False
        }
    except Exception as e:
        print(f"[ERROR] Whisper transcription failed: {e}")
        sys.stdout.flush()
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'text': '',
            'error': 'Transcription error occurred',
            'is_music_only': False
        }


def download_youtube_video(url, output_dir):
    """
    Download a YouTube video using yt-dlp with validation.
    Returns: Path to downloaded video or None if failed.
    """
    import time
    try:
        import yt_dlp
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        video_id = _video_id_from_url(url)
        if not video_id:
            print("[ERROR] Could not extract video ID from URL")
            sys.stdout.flush()
            return None
            
        output_template = os.path.join(output_dir, f"{video_id}.%(ext)s")
        
        ydl_opts = {
            'format': 'bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4][height<=720]/best[height<=720]',
            'outtmpl': output_template,
            'quiet': False,  # Enable output for debugging
            'no_warnings': False,
            'merge_output_format': 'mp4',  # Force mp4 output
            'postprocessor_args': [
                '-movflags', 'faststart',  # Optimize for streaming
            ],
        }
        
        print(f"[YOUTUBE] Downloading video: {url}")
        sys.stdout.flush()
        
        video_path = None
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=True)
                video_path = ydl.prepare_filename(info)
                
                # Handle merged filename (yt-dlp might add .mp4 extension)
                if not os.path.exists(video_path):
                    # Try with .mp4 extension
                    base = os.path.splitext(video_path)[0]
                    video_path = base + '.mp4'
                
            except Exception as dl_error:
                print(f"[ERROR] Download extraction failed: {dl_error}")
                sys.stdout.flush()
                return None
        
        # Wait a moment for file system to sync
        time.sleep(1)
        
        # Validate the downloaded file
        if not video_path or not os.path.exists(video_path):
            print(f"[ERROR] Downloaded file not found: {video_path}")
            sys.stdout.flush()
            return None
        
        # Check file size is reasonable (> 1KB)
        file_size = os.path.getsize(video_path)
        if file_size < 1024:
            print(f"[ERROR] Downloaded file too small ({file_size} bytes), likely corrupted")
            sys.stdout.flush()
            try:
                os.remove(video_path)
            except:
                pass
            return None
        
        # Verify file can be opened by cv2
        import cv2
        cap = cv2.VideoCapture(video_path)
        is_valid = cap.isOpened()
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        
        if not is_valid or frame_count <= 0:
            print(f"[ERROR] Downloaded video is corrupted or unreadable (frames={frame_count})")
            sys.stdout.flush()
            try:
                os.remove(video_path)
            except:
                pass
            return None
        
        print(f"[YOUTUBE] ✓ Video downloaded successfully: {video_path} ({file_size} bytes, {frame_count} frames)")
        sys.stdout.flush()
        return video_path
        
    except Exception as e:
        print(f"[ERROR] YouTube download failed: {e}")
        sys.stdout.flush()
        import traceback
        traceback.print_exc()
        return None



def _video_id_from_url(url):
    """Extract YouTube video ID from URL - supports regular videos and Shorts"""
    if not url or not isinstance(url, str):
        return None
    url = url.strip()
    
    # Remove any query parameters after video ID for shorts
    # youtube.com/shorts/ID?si=xxx -> shorts/ID
    url_clean = url.split('?')[0] if '?' in url else url
    
    # Match patterns:
    # 1. youtube.com/watch?v=ID
    # 2. youtu.be/ID
    # 3. youtube.com/shorts/ID (NEW - for YouTube Shorts)
    m = re.search(
        r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)([a-zA-Z0-9_-]{11})",
        url_clean
    )
    if m:
        return m.group(1)
    
    # Direct video ID
    if re.fullmatch(r"[a-zA-Z0-9_-]{11}", url):
        return url
    
    return None


def _get_transcript(video_id):
    """Fetch transcript for a YouTube video - tries multiple languages"""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        
        # Try different language codes in order of preference
        language_codes = [
            ['en'],           # English
            ['en-US'],        # English (US)
            ['en-GB'],        # English (UK)
            ['a.en'],         # Auto-generated English
            ['te'],           # Telugu
            ['hi'],           # Hindi
            ['ta'],           # Tamil
        ]
        
        transcript_text = None
        last_error = None
        
        for lang_code in language_codes:
            try:
                print(f"[YOUTUBE] Trying to fetch transcript with language: {lang_code}")
                sys.stdout.flush()
                from youtube_transcript_api import YouTubeTranscriptApi
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=lang_code)
                transcript_text = ' '.join([entry['text'] for entry in transcript_list])
                print(f"[YOUTUBE] ✓ Successfully fetched transcript in {lang_code}, length={len(transcript_text)} chars")
                sys.stdout.flush()
                return transcript_text
            except Exception as e:
                last_error = str(e)
                continue
        
        # If all languages failed, try getting any available transcript
        try:
            print("[YOUTUBE] Trying to fetch any available transcript...")
            sys.stdout.flush()
            from youtube_transcript_api import YouTubeTranscriptApi
            # Try without specifying language - gets any available
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = ' '.join([entry['text'] for entry in transcript_list])
            print(f"[YOUTUBE] ✓ Fetched transcript, length={len(transcript_text)} chars")
            sys.stdout.flush()
            return transcript_text
        except Exception as e:
            last_error = str(e)
        
        print(f"[ERROR] Could not fetch transcript for video {video_id}: {last_error}")
        sys.stdout.flush()
        return None
        
    except Exception as e:
        print(f"[ERROR] Transcript fetch failed: {e}")
        sys.stdout.flush()
        return None


def _get_video_title(video_id):
    """Fetch video title from YouTube"""
    try:
        import requests
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        response = requests.get(oembed_url, timeout=5)
        if response.status_code == 200:
            title = response.json().get('title', '')
            print(f"[YOUTUBE] Video title: {title}")
            sys.stdout.flush()
            return title
    except Exception as e:
        print(f"[YOUTUBE] Could not fetch title: {e}")
        sys.stdout.flush()
    return ""


def _extract_key_points(text, num_points=5):
    """Extract key points from text using sentence importance"""
    sentences = [s.strip() for s in text.replace('\n', ' ').split('.') if len(s.strip()) > 20]
    
    if not sentences:
        return []
    
    # Simple heuristic: longer sentences often contain more information
    # and sentences with certain keywords are more important
    # FIX 4: Added Telugu keywords for better Telugu summary extraction
    important_keywords = [
        # English keywords
        'important', 'key', 'main', 'first', 'second', 'finally', 
        'conclusion', 'summary', 'example', 'because', 'therefore',
        # Telugu keywords (transliterated)
        'ముఖ్యమైన', 'ముఖ్య', 'మొదటి', 'రెండవ', 'చివరగా',
        'ఉదాహరణ', 'ఎందుకంటే', 'కారణంగా', 'అంటే', 'సారాంశం'
    ]
    
    scored_sentences = []
    for sent in sentences:
        score = len(sent.split())  # Length score
        sent_lower = sent.lower()
        # Bonus for important keywords
        for keyword in important_keywords:
            if keyword in sent_lower or keyword in sent:  # Check both for Telugu
                score += 10
        scored_sentences.append((score, sent))
    
    # Sort by score and take top N
    scored_sentences.sort(reverse=True, key=lambda x: x[0])
    key_points = [sent for score, sent in scored_sentences[:num_points]]
    
    return key_points


def _generate_simple_summary(transcript, video_title=None, language='english'):
    """
    Generate a simple, easy-to-understand summary from a transcript.
    
    Supports Telugu and English output.
    
    Format:
    - Main topic
    - Key points (bullet points)
    - Important examples/facts
    - Specific constraints: No timestamps, no personal opinions.
    """
    try:
        # Clean transcript of any timestamp-like patterns
        clean_transcript = re.sub(r'\[\d+:\d+\]', '', transcript)
        
        # Extract key points from original transcript (extractive approach)
        key_points = _extract_key_points(clean_transcript, num_points=8)
        
        # Create a concise summary from the first part of transcript
        sentences = [s.strip() + '.' for s in clean_transcript.split('.') if len(s.strip()) > 30]
        main_idea_sentences = sentences[:3] if len(sentences) >= 3 else sentences
        main_idea = ' '.join(main_idea_sentences)
        
        # Format based on language
        if language == 'telugu':
            return _format_telugu_summary(main_idea, key_points, clean_transcript, video_title)
        else:
            return _format_english_summary(main_idea, key_points, clean_transcript, video_title)

    except Exception as e:
        print(f"[ERROR] Summary generation failed: {e}")
        sys.stdout.flush()
        return "(Could not generate detailed summary)"


def _format_telugu_summary(main_idea, key_points, transcript, video_title=None):
    """Format summary in Telugu language"""
    output = []
    
    if video_title:
        output.append(f"వీడియో శీర్షిక: {video_title}\n")
    
    output.append("ముఖ్య విషయం:")
    output.append(f"  {main_idea}")
    output.append("")
    
    if key_points:
        output.append("ముఖ్య అంశాలు:")
        for i, point in enumerate(key_points, 1):
            point = point.strip()
            if not point.endswith('.'):
                point += '.'
            output.append(f"  • {point}")
        output.append("")
    
    # Extract important facts
    first_part = ' '.join(transcript.split()[:500])
    facts = [s.strip() + '.' for s in first_part.split('.') 
            if any(word in s.lower() for word in ['fact', 'discovered', 'result', 'research', 'shows', 'found'])]
    
    if not facts:
        facts = [s.strip() + '.' for s in first_part.split('.') 
                if any(word in s.lower() for word in ['example', 'for instance', 'such as'])]

    if facts:
        output.append("ముఖ్యమైన వాస్తవాలు & ఉదాహరణలు:")
        for fact in facts[:3]:
            if len(fact) > 10:
                output.append(f"  • {fact}")
        output.append("")
    
    return '\n'.join(output)


def _format_english_summary(main_idea, key_points, transcript, video_title=None):
    """Format summary in English language"""
    output = []
    
    if video_title:
        output.append(f"VIDEO TITLE: {video_title}\n")
    
    output.append("MAIN IDEA:")
    output.append(f"  {main_idea}")
    output.append("")
    
    if key_points:
        output.append("KEY POINTS:")
        for i, point in enumerate(key_points, 1):
            point = point.strip()
            if not point.endswith('.'):
                point += '.'
            output.append(f"  • {point}")
        output.append("")
    
    # Highlight important facts
    first_part = ' '.join(transcript.split()[:500])
    facts = [s.strip() + '.' for s in first_part.split('.') 
            if any(word in s.lower() for word in ['fact', 'discovered', 'result', 'research', 'shows', 'found'])]
    
    if not facts:
        facts = [s.strip() + '.' for s in first_part.split('.') 
                if any(word in s.lower() for word in ['example', 'for instance', 'such as'])]

    if facts:
        output.append("IMPORTANT FACTS & EXAMPLES:")
        for fact in facts[:3]:
            if len(fact) > 10:
                output.append(f"  • {fact}")
        output.append("")
    
    return '\n'.join(output)



def summarize_youtube_simple(url_or_video_id, language='english'):
    """
    Main entry point for YouTube summarization (simple version).
    Returns a dictionary with summary, transcript, and metadata.
    Supports Telugu and English output.
    """
    try:
        print("[YOUTUBE] Starting simple summarization...")
        sys.stdout.flush()

        # If it looks like a URL, extract video_id; otherwise use it as-is
        video_id = _video_id_from_url(url_or_video_id)
        if not video_id:
            video_id = url_or_video_id

        # Get transcript (captions first, fallback to Whisper)
        try:
            transcript_text = _get_transcript(video_id)
        except Exception as e:
            print(f"[ERROR] Exception getting transcript: {e}")
            sys.stdout.flush()
            transcript_text = None

        if not transcript_text:
            print("[YOUTUBE] Captions not available. Attempting Whisper transcription...")
            sys.stdout.flush()
            
            # Download audio for Whisper
            temp_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'temp_audio')
            audio_path = download_youtube_audio(url_or_video_id, temp_dir)
            
            if audio_path:
                # Pass the selected language to Whisper with validation
                whisper_result = whisper_transcribe(audio_path, language=language)
                
                # Check if transcription succeeded
                if not whisper_result.get('success', False):
                    # Music-only or insufficient speech detected
                    error_message = whisper_result.get('error', 'Transcription failed')
                    print(f"[WHISPER] ✗ Transcription validation failed: {error_message}")
                    sys.stdout.flush()
                    
                    # Clean up audio file
                    try:
                        if os.path.exists(audio_path):
                            os.remove(audio_path)
                    except:
                        pass
                    
                    return {
                        'success': False,
                        'error': error_message
                    }
                
                # Extract validated transcript text
                transcript_text = whisper_result.get('text', '')
                
                # Clean up audio file safely
                try:
                    if os.path.exists(audio_path):
                        os.remove(audio_path)
                        print(f"[CLEANUP] ✓ Removed temporary audio file")
                        sys.stdout.flush()
                except Exception as cleanup_error:
                    print(f"[WARNING] Could not remove audio file: {cleanup_error}")
                    sys.stdout.flush()
            
            if not transcript_text:
                return {
                    'success': False,
                    'error': 'Could not fetch transcript (captions disabled) and Whisper transcription failed.'
                }

        # Get video title
        video_title = _get_video_title(video_id)

        # Generate summary with language support
        summary = _generate_simple_summary(transcript_text, video_title, language)

        return {
            'success': True,
            'summary': summary,
            'transcript': transcript_text,
            'video_id': video_id,
            'video_title': video_title
        }

    except Exception as e:
        print(f"[ERROR] YouTube summarization failed: {e}")
        sys.stdout.flush()
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }


# Backward compatibility
def summarize_youtube(url_or_video_id):
    """Original function for compatibility"""
    result = summarize_youtube_simple(url_or_video_id)
    return {
        'summary': result['summary'],
        'transcript': result['transcript'],
        'error': result['error']
    }
