"""
Smart video cutter with narrated summarization.
Analyzes video content, generates a text summary, adds natural voice-over,
and creates an edited video with selected scenes.
"""
import os
import sys
import tempfile
import asyncio
import traceback
from typing import Optional, Dict, List, Tuple

# Import existing modules
from .auto_caption import transcribe_video


def _generate_summary_text(transcript: str) -> str:
    """Generate a cohesive summary from the transcript using BART."""
    try:
        from transformers import pipeline
        
        # Initialize summarizer
        summarizer = pipeline('summarization', model='facebook/bart-large-cnn')
        
        # BART has a max token limit, so chunk if needed
        max_chunk = 1024
        chunks = []
        words = transcript.split()
        
        for i in range(0, len(words), max_chunk):
            chunk = ' '.join(words[i:i + max_chunk])
            if len(chunk.strip()) > 50:  # Only summarize meaningful chunks
                result = summarizer(chunk, max_length=150, min_length=30, do_sample=False)
                chunks.append(result[0]['summary_text'])
        
        # Combine all summaries
        summary = ' '.join(chunks)
        
        # Make it more conversational for voice-over
        summary = summary.replace('. ', '. \n')  # Add pauses
        
        return summary
    except Exception as e:
        # Fallback: just use first portion of transcript
        return transcript[:500] + "..."


async def _generate_voiceover(text: str, output_path: str) -> Optional[str]:
    """Generate natural voice-over using edge-tts."""
    try:
        import edge_tts
        
        print(f"[TTS] Starting edge-tts voice generation...")
        print(f"[TTS] Text length: {len(text)} characters")
        print(f"[TTS] Output path: {output_path}")
        sys.stdout.flush()
        
        # Use a natural-sounding voice
        voice = "en-US-GuyNeural"  # Calm, professional male voice
        # Alternative: "en-US-AriaNeural" for female voice
        
        print(f"[TTS] Using voice: {voice}")
        sys.stdout.flush()
        
        communicate = edge_tts.Communicate(text, voice)
        
        print(f"[TTS] Saving audio to file...")
        sys.stdout.flush()
        await communicate.save(output_path)
        
        print(f"[TTS] Save completed")
        sys.stdout.flush()
        
        # Verify file was created
        if os.path.isfile(output_path):
            file_size = os.path.getsize(output_path)
            print(f"[TTS] ✓ Audio file created successfully: {file_size} bytes")
            sys.stdout.flush()
            return output_path
        else:
            print(f"[TTS] ✗ Audio file was not created at: {output_path}")
            sys.stdout.flush()
            return None
            
    except Exception as e:
        print(f"[TTS] ✗ Voice-over generation failed!")
        print(f"[TTS] Error type: {type(e).__name__}")
        print(f"[TTS] Error message: {str(e)}")
        print(f"[TTS] Full traceback:")
        traceback.print_exc()
        sys.stdout.flush()
        return None


def _get_audio_duration(audio_path: str) -> float:
    """Get duration of audio file in seconds with multiple fallback methods."""
    import wave
    import contextlib
    
    # Check if file exists
    if not os.path.isfile(audio_path):
        print(f"Audio file not found: {audio_path}")
        return 0.0
    
    # Check file size
    file_size = os.path.getsize(audio_path)
    print(f"Audio file size: {file_size} bytes")
    if file_size == 0:
        print("Audio file is empty!")
        return 0.0
    
    # Method 1: Try wave module for WAV files
    try:
        with contextlib.closing(wave.open(audio_path, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
            print(f"Audio duration (wave): {duration}s")
            if duration > 0:
                return duration
    except Exception as e:
        print(f"Wave method failed: {e}")
    
    # Method 2: Try moviepy
    try:
        from moviepy.editor import AudioFileClip
        clip = AudioFileClip(audio_path)
        duration = clip.duration
        clip.close()
        print(f"Audio duration (moviepy): {duration}s")
        if duration and duration > 0:
            return duration
    except Exception as e:
        print(f"MoviePy method failed: {e}")
    
    # Method 3: Use mutagen for MP3/other formats
    try:
        from mutagen.mp3 import MP3
        audio = MP3(audio_path)
        duration = audio.info.length
        print(f"Audio duration (mutagen): {duration}s")
        if duration > 0:
            return duration
    except Exception as e:
        print(f"Mutagen method failed: {e}")
    
    # Method 4: Estimate from file size (very rough)
    # MP3 at 128 kbps ≈ 16 KB/s, so duration ≈ file_size / 16000
    estimated = file_size / 16000.0
    print(f"Estimated duration from file size: {estimated}s")
    return max(estimated, 10.0)  # Return at least 10 seconds


def _select_video_clips(video_path: str, segments: List[Dict], target_duration: float) -> List[Tuple[float, float]]:
    """
    Select important video segments to match the narration duration.
    Returns list of (start_time, end_time) tuples.
    """
    try:
        from moviepy.editor import VideoFileClip
        
        video = VideoFileClip(video_path)
        total_duration = video.duration
        video.close()
        
        # Strategy: Select segments evenly distributed across the video
        # to give a comprehensive overview
        
        if not segments or len(segments) == 0:
            # Fallback: divide video into equal parts
            num_clips = max(3, int(target_duration / 10))  # ~10 sec per clip
            interval = total_duration / num_clips
            clips = []
            for i in range(num_clips):
                start = i * interval
                end = min(start + 8, total_duration)  # 8 sec clips
                clips.append((start, end))
            
            # Adjust to match target duration
            total_clip_duration = sum(e - s for s, e in clips)
            if total_clip_duration < target_duration:
                # Extend clips proportionally
                factor = target_duration / total_clip_duration
                clips = [(s, min(s + (e - s) * factor, total_duration)) for s, e in clips]
            
            return clips[:int(target_duration / 5)]  # Ensure we don't exceed
        
        # Use transcript segments to select meaningful clips
        clips = []
        for seg in segments:
            ts = seg.get('timestamp')
            if ts and len(ts) >= 2:
                start, end = float(ts[0]), float(ts[1])
                clips.append((start, end))
        
        # Sort by start time
        clips.sort(key=lambda x: x[0])
        
        # Select clips to match target duration
        selected = []
        current_duration = 0
        
        for start, end in clips:
            clip_duration = end - start
            if current_duration + clip_duration <= target_duration:
                selected.append((start, end))
                current_duration += clip_duration
            elif current_duration < target_duration:
                # Add partial clip to reach target
                remaining = target_duration - current_duration
                selected.append((start, start + remaining))
                break
        
        return selected if selected else [(0, min(target_duration, total_duration))]
        
    except Exception as e:
        print(f"Clip selection error: {e}")
        # Fallback
        return [(0, min(target_duration, 60))]


def _create_edited_video(video_path: str, clips: List[Tuple[float, float]], voiceover_path: str, output_path: str) -> bool:
    """Create final video by combining selected clips with voice-over."""
    try:
        print(f"Creating video with {len(clips)} clips")
        sys.stdout.flush()
        
        from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips
        
        print("Loading source video...")
        sys.stdout.flush()
        video = VideoFileClip(video_path)
        
        print(f"Source video: {video.duration}s, {video.size}")
        sys.stdout.flush()
        
        # Extract video clips (without original audio)
        print("Extracting clips...")
        sys.stdout.flush()
        video_clips = []
        for i, (start, end) in enumerate(clips):
            print(f"  Clip {i+1}/{len(clips)}: {start:.1f}s - {end:.1f}s")
            sys.stdout.flush()
            clip = video.subclipped(start, end).without_audio()
            video_clips.append(clip)
        
        # Concatenate video clips
        print("Concatenating clips...")
        sys.stdout.flush()
        if len(video_clips) > 1:
            final_video = concatenate_videoclips(video_clips, method="compose")
        else:
            final_video = video_clips[0]
        
        print(f"Final video duration before audio: {final_video.duration}s")
        sys.stdout.flush()
        
        # Add voice-over audio
        print("Loading voice-over...")
        sys.stdout.flush()
        voiceover = AudioFileClip(voiceover_path)
        print(f"Voice-over duration: {voiceover.duration}s")
        sys.stdout.flush()
        
        # Match durations
        if final_video.duration > voiceover.duration:
            print(f"Trimming video from {final_video.duration}s to {voiceover.duration}s")
            sys.stdout.flush()
            final_video = final_video.subclipped(
0, voiceover.duration)
        elif final_video.duration < voiceover.duration:
            print(f"Trimming audio from {voiceover.duration}s to {final_video.duration}s")
            sys.stdout.flush()
            voiceover = voiceover.subclipped(0, final_video.duration)
        
        print("Setting audio track...")
        sys.stdout.flush()
        final_video = final_video.with_audio(voiceover)
        # Write output with simpler settings
        print(f"Writing output video to {output_path}...")
        sys.stdout.flush()
        
        final_video.write_videofile(
    output_path,
    codec='libx264',
    audio_codec='aac'
)

        
        print("Cleaning up resources...")
        sys.stdout.flush()
        
        # Cleanup
        final_video.close()
        video.close()
        voiceover.close()
        
        for clip in video_clips:
            try:
                clip.close()
            except:
                pass
        
        print("Video creation complete!")
        sys.stdout.flush()
        return True
        
    except Exception as e:
        print(f"\n❌ VIDEO CREATION ERROR: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print(f"\nFull traceback:")
        traceback.print_exc()
        sys.stdout.flush()
        return False


def create_narrated_summary(video_path: str, output_path: str) -> Dict[str, any]:
    """
    Main function to create a narrated video summary.
    
    Returns:
        {
            'success': bool,
            'summary_text': str,
            'output_video': str,
            'error': str or None
        }
    """
    try:
        print("Step 1/5: Transcribing video...")
        # 1. Transcribe video
        transcript_result = transcribe_video(video_path)
        
        if transcript_result.get('error'):
            return {
                'success': False,
                'summary_text': '',
                'output_video': '',
                'error': f"Transcription failed: {transcript_result['error']}"
            }
        
        transcript_text = transcript_result.get('text', '')
        segments = transcript_result.get('segments', [])
        
        if not transcript_text or len(transcript_text.strip()) < 50:
            return {
                'success': False,
                'summary_text': '',
                'output_video': '',
                'error': "Transcript too short or empty. Please use a video with clear speech."
            }
        
        print("Step 2/5: Generating summary...")
        # 2. Generate summary text
        summary_text = _generate_summary_text(transcript_text)
        
        print("Step 3/5: Creating voice-over narration...")
        # 3. Generate voice-over
        voiceover_path = tempfile.mktemp(suffix='.mp3')
        
        print(f"Generating TTS audio to: {voiceover_path}")
        print(f"Summary text length: {len(summary_text)} chars")
        
        # Run async function
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            voiceover_result = loop.run_until_complete(_generate_voiceover(summary_text, voiceover_path))
            loop.close()
        except Exception as e:
            print(f"TTS generation exception: {e}")
            voiceover_result = None
        
        if not voiceover_result or not os.path.isfile(voiceover_path):
            error_msg = "Voice-over generation failed. "
            if not os.path.isfile(voiceover_path):
                error_msg += "Audio file was not created. "
            error_msg += "Please check your internet connection (edge-tts requires internet)."
            return {
                'success': False,
                'summary_text': summary_text,
                'output_video': '',
                'error': error_msg
            }
        
        print(f"Voice-over created: {os.path.getsize(voiceover_path)} bytes")
        
        print("Step 4/5: Selecting video clips...")
        # 4. Get voice-over duration and select matching video clips
        voiceover_duration = _get_audio_duration(voiceover_path)
        
        print(f"Detected voice-over duration: {voiceover_duration}s")
        
        if voiceover_duration <= 0:
            os.remove(voiceover_path)
            return {
                'success': False,
                'summary_text': summary_text,
                'output_video': '',
                'error': f"Could not determine voice-over duration. File exists: {os.path.isfile(voiceover_path)}, Size: {os.path.getsize(voiceover_path) if os.path.isfile(voiceover_path) else 0} bytes. Please check terminal output for details."
            }
        
        print(f"Selecting clips for {voiceover_duration}s narration...")
        sys.stdout.flush()
        clips = _select_video_clips(video_path, segments, voiceover_duration)
        print(f"Selected {len(clips)} clips: {clips}")
        sys.stdout.flush()
        
        print("Step 5/5: Creating final video...")
        sys.stdout.flush()
        # 5. Create final video
        success = _create_edited_video(video_path, clips, voiceover_path, output_path)
        print(f"Video creation result: {success}")
        sys.stdout.flush()
        
        # Cleanup temp files
        try:
            os.remove(voiceover_path)
        except OSError:
            pass
        
        if success:
            return {
                'success': True,
                'summary_text': summary_text,
                'output_video': output_path,
                'error': None
            }
        else:
            return {
                'success': False,
                'summary_text': summary_text,
                'output_video': '',
                'error': "Failed to create final video."
            }
            
    except Exception as e:
        return {
            'success': False,
            'summary_text': '',
            'output_video': '',
            'error': f"Unexpected error: {str(e)}"
        }
