"""
Smart video editor that removes unnecessary parts while keeping original audio.
Analyzes transcript to identify key moments and creates a trimmed version
with the speaker's original voice.
"""
import os
import sys
import traceback
from typing import List, Tuple, Dict

from .auto_caption import transcribe_video


def _analyze_important_segments(segments: List[Dict], full_text: str) -> List[Tuple[float, float]]:
    """
    Analyze transcript segments to identify important parts.
    Returns list of (start, end) timestamps to keep.
    """
    if not segments:
        return []
    
    important_clips = []
    
    # Strategy: Keep segments that contain meaningful content
    # Filter out: long pauses, filler words, repetitive content
    
    filler_phrases = ['um', 'uh', 'like', 'you know', 'so', 'basically', 'actually']
    
    for seg in segments:
        text = seg.get('text', '').strip().lower()
        timestamp = seg.get('timestamp')
        
        if not timestamp or len(timestamp) < 2:
            continue
            
        start, end = float(timestamp[0]), float(timestamp[1])
        duration = end - start
        
        # Skip very short segments (likely noise)
        if duration < 0.5:
            continue
        
        # Skip segments that are mostly filler
        words = text.split()
        if len(words) > 0:
            filler_count = sum(1 for w in words if w in filler_phrases)
            filler_ratio = filler_count / len(words)
            
            # Keep if less than 70% filler
            if filler_ratio < 0.7 and len(text) > 3:
                important_clips.append((start, end))
    
    return important_clips


def _merge_adjacent_clips(clips: List[Tuple[float, float]], max_gap: float = 1.0) -> List[Tuple[float, float]]:
    """
    Merge clips that are close together to avoid choppy editing.
    max_gap: maximum gap in seconds to bridge between clips
    """
    if not clips:
        return []
    
    # Sort by start time
    sorted_clips = sorted(clips, key=lambda x: x[0])
    
    merged = [sorted_clips[0]]
    
    for start, end in sorted_clips[1:]:
        last_start, last_end = merged[-1]
        
        # If gap is small, merge
        if start - last_end <= max_gap:
            merged[-1] = (last_start, end)
        else:
            merged.append((start, end))
    
    return merged


def create_smart_edit(video_path: str, output_path: str, target_ratio: float = 0.5) -> Dict:
    """
    Create an intelligently edited version of the video with original audio.
    Removes unnecessary parts while keeping the speaker's voice.
    
    Args:
        video_path: Path to input video
        output_path: Path for output video
        target_ratio: Target length as ratio of original (0.5 = 50% of original)
    
    Returns:
        {
            'success': bool,
            'summary_text': str,  # Text summary of what was kept
            'output_video': str,
            'original_duration': float,
            'edited_duration': float,
            'error': str or None
        }
    """
    try:
        print("[SMART EDIT] Step 1/4: Analyzing video content...")
        sys.stdout.flush()
        
        # 1. Transcribe to understand content
        transcript_result = transcribe_video(video_path)
        
        if transcript_result.get('error'):
            return {
                'success': False,
                'summary_text': '',
                'output_video': '',
                'original_duration': 0,
                'edited_duration': 0,
                'error': f"Could not analyze video: {transcript_result['error']}"
            }
        
        segments = transcript_result.get('segments', [])
        full_text = transcript_result.get('text', '')
        
        if not segments or len(full_text.strip()) < 20:
            return {
                'success': False,
                'summary_text': '',
                'output_video': '',
                'original_duration': 0,
                'edited_duration': 0,
                'error': "Video has insufficient speech content for smart editing."
            }
        
        print(f"   Found {len(segments)} speech segments")
        sys.stdout.flush()
        
        print("[SMART EDIT] Step 2/4: Identifying key moments...")
        sys.stdout.flush()
        
        # 2. Identify important segments
        important_clips = _analyze_important_segments(segments, full_text)
        
        if not important_clips:
            return {
                'success': False,
                'summary_text': full_text,
                'output_video': '',
                'original_duration': 0,
                'edited_duration': 0,
                'error': "Could not identify any key segments to keep."
            }
        
        print(f"   Identified {len(important_clips)} important segments")
        sys.stdout.flush()
        
        # 3. Merge adjacent clips for smooth editing
        merged_clips = _merge_adjacent_clips(important_clips, max_gap=1.5)
        print(f"   Merged into {len(merged_clips)} smooth sections")
        sys.stdout.flush()
        
        print("[SMART EDIT] Step 3/4: Loading video...")
        sys.stdout.flush()
        
        from moviepy import VideoFileClip, concatenate_videoclips
        
        video = VideoFileClip(video_path)
        original_duration = video.duration
        
        print(f"   Original video: {original_duration:.1f}s")
        sys.stdout.flush()
        
        # 4. Extract clips WITH original audio
        print("[SMART EDIT] Step 4/4: Creating edited video...")
        sys.stdout.flush()
        
        video_clips = []
        total_kept = 0
        
        for i, (start, end) in enumerate(merged_clips):
            print(f"   Extracting clip {i+1}/{len(merged_clips)}: {start:.1f}s - {end:.1f}s")
            sys.stdout.flush()
            
            # Keep FULL clip with original audio
            clip = video.subclipped(start, end)
            video_clips.append(clip)
            total_kept += (end - start)
        
        print(f"   Total content kept: {total_kept:.1f}s ({total_kept/original_duration*100:.1f}%)")
        sys.stdout.flush()
        
        # 5. Concatenate clips
        print("   Joining clips...")
        sys.stdout.flush()
        
        if len(video_clips) > 1:
            final_video = concatenate_videoclips(video_clips, method="compose")
        else:
            final_video = video_clips[0]
        
        edited_duration = final_video.duration
        
        # 6. Write output
        print(f"   Writing output video ({edited_duration:.1f}s)...")
        sys.stdout.flush()
        
        final_video.write_videofile(
    output_path,
    codec='libx264',
    audio_codec='aac'
)
        # 7. Cleanup
        print("   Cleaning up...")
        sys.stdout.flush()
        
        final_video.close()
        video.close()
        for clip in video_clips:
            try:
                clip.close()
            except:
                pass
        
        # Create summary
        reduction = (1 - edited_duration / original_duration) * 100
        summary_text = f"""Smart Edit Complete!

Original Duration: {original_duration:.1f} seconds
Edited Duration: {edited_duration:.1f} seconds
Reduction: {reduction:.1f}% shorter

The video has been intelligently edited to remove pauses, filler words, and less important content while preserving the speaker's original voice and maintaining natural pacing.

Key segments kept: {len(merged_clips)}"""
        
        print("[SUCCESS] Smart edit complete!")
        sys.stdout.flush()
        
        return {
            'success': True,
            'summary_text': summary_text,
            'output_video': output_path,
            'original_duration': original_duration,
            'edited_duration': edited_duration,
            'error': None
        }
        
    except Exception as e:
        print(f"\n[ERROR] SMART EDIT ERROR: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print(f"\nFull traceback:")
        traceback.print_exc()
        sys.stdout.flush()
        
        return {
            'success': False,
            'summary_text': '',
            'output_video': '',
            'original_duration': 0,
            'edited_duration': 0,
            'error': f"Smart edit failed: {str(e)}"
        }
