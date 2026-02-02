import os
import sys

# Ensure project root is in path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from flask import Flask, abort, render_template, request, send_from_directory
from summarizer.video_summarizer import summarize_video
from summarizer.auto_caption import transcribe_video
from summarizer.smart_cutter import create_narrated_summary
from summarizer.smart_edit import create_smart_edit
from summarizer.youtube_simple import summarize_youtube_simple

app = Flask(__name__)

# Production configuration
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['ENV'] = os.getenv('FLASK_ENV', 'production')

UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.isfile(path):
        return abort(404)
    mime = None
    if filename.lower().endswith(".mp4"):
        mime = "video/mp4"
    elif filename.lower().endswith(".webm"):
        mime = "video/webm"
    return send_from_directory(UPLOAD_FOLDER, filename, mimetype=mime)

@app.route("/Backend_Documentation.pdf")
def download_pdf():
    return send_from_directory(os.path.dirname(__file__), "Backend_Documentation.pdf", as_attachment=True)

@app.route("/", methods=["GET", "POST"])
def index():
    return handle_request('index.html')

def handle_request(template_name):
    # Video flow
    summary = ""
    output_video = ""
    caption_text = ""
    caption_srt = ""
    narrated_summary = ""
    narrated_video = ""
    smart_edit_summary = ""
    smart_edit_video = ""
    # YouTube flow
    youtube_summary = ""
    youtube_transcript = ""
    youtube_title = ""
    # Common
    msg = ""
    msg_type = "success"  # success | error

    if request.method == "POST":
        video_file = request.files.get("video_file")
        do_summary = request.form.get("do_summary") == "on"
        do_caption = request.form.get("do_caption") == "on"
        do_narrated = request.form.get("do_narrated") == "on"
        do_smart_edit = request.form.get("do_smart_edit") == "on"

        # ---- Video: summarize and/or auto-caption ----
        if video_file and video_file.filename:
            if not do_summary and not do_caption and not do_narrated and not do_smart_edit:
                msg = "Please select at least one processing option."
                msg_type = "error"
            else:
                try:
                    input_path = os.path.join(UPLOAD_FOLDER, video_file.filename)
                    video_file.save(input_path)

                    if do_summary:
                        output_path = os.path.join(UPLOAD_FOLDER, "summary_video.mp4")
                        summary = summarize_video(input_path, output_path)
                        output_video = "summary_video.mp4"

                    if do_caption:
                        cap = transcribe_video(input_path)
                        if cap.get("error"):
                            if msg:
                                msg += " "
                            msg += "Caption: " + cap["error"]
                            msg_type = "error"
                        else:
                            caption_text = cap.get("text", "")
                            caption_srt = cap.get("srt", "")

                    if do_narrated:
                        narrated_output = os.path.join(UPLOAD_FOLDER, "narrated_summary.mp4")
                        result = create_narrated_summary(input_path, narrated_output)
                        if result.get("success"):
                            narrated_summary = result.get("summary_text", "")
                            narrated_video = "narrated_summary.mp4"
                            if not msg:
                                msg = "Narrated summary created successfully!"
                        else:
                            if msg:
                                msg += " "
                            msg += "Narrated Summary: " + (result.get("error") or "Unknown error")
                            msg_type = "error"

                    if do_smart_edit:
                        smart_edit_output = os.path.join(UPLOAD_FOLDER, "smart_edit.mp4")
                        result = create_smart_edit(input_path, smart_edit_output)
                        if result.get("success"):
                            smart_edit_summary = result.get("summary_text", "")
                            smart_edit_video = "smart_edit.mp4"
                            if not msg:
                                msg = "Smart edit created successfully!"
                        else:
                            if msg:
                                msg += " "
                            msg += "Smart Edit: " + (result.get("error") or "Unknown error")
                            msg_type = "error"

                    if msg_type != "error" and not msg:
                        msg = "Video processed successfully!"
                        msg_type = "success"

                except Exception as e:
                    msg = "Error processing video: " + str(e)
                    msg_type = "error"
        elif request.form.get("youtube_url"):
            youtube_url = request.form.get("youtube_url")
            summary_language = request.form.get("summary_language", "english")
            try:
                print(f"[YOUTUBE] Processing: {youtube_url} (Language: {summary_language})")
                from summarizer.youtube_simple import download_youtube_video
                
                # 1. Get Text Summary with language support
                result = summarize_youtube_simple(youtube_url, language=summary_language)
                if result.get("success"):
                    youtube_summary = result.get("summary", "")
                    youtube_transcript = result.get("transcript", "")
                    youtube_title = result.get("video_title", "")
                    
                    # 2. Try to get Video Summary (Download & Process)
                    print("[YOUTUBE] Attempting video download for visual summary...")
                    sys.stdout.flush()
                    video_dl_path = download_youtube_video(youtube_url, UPLOAD_FOLDER)
                    
                    if video_dl_path and os.path.exists(video_dl_path):
                        print(f"[YOUTUBE] Video downloaded to {video_dl_path}. Generating visual summary...")
                        sys.stdout.flush()
                        
                        try:
                            # Use a unique name for the summary or reuse summary_video.mp4
                            output_path = os.path.join(UPLOAD_FOLDER, "youtube_summary_video.mp4")
                            video_summary_text = summarize_video(video_dl_path, output_path)
                            
                            # Only set output_video if summarization succeeded
                            if os.path.exists(output_path):
                                output_video = "youtube_summary_video.mp4"
                                print(f"[YOUTUBE] ✓ Visual summary created: {output_path}")
                                sys.stdout.flush()
                            
                            # Cleanup the full downloaded video to save space
                            try:
                                if os.path.exists(video_dl_path):
                                    os.remove(video_dl_path)
                                    print(f"[CLEANUP] ✓ Removed downloaded video")
                                    sys.stdout.flush()
                            except Exception as cleanup_err:
                                print(f"[WARNING] Could not remove video: {cleanup_err}")
                                sys.stdout.flush()
                        except Exception as summary_err:
                            print(f"[ERROR] Video summarization failed: {summary_err}")
                            sys.stdout.flush()
                            # Clean up on error
                            try:
                                if os.path.exists(video_dl_path):
                                    os.remove(video_dl_path)
                            except:
                                pass
                    else:
                        print("[YOUTUBE] Video download failed or was invalid, skipping visual summary")
                        sys.stdout.flush()
                        
                    msg = "YouTube video summarized successfully!"
                    msg_type = "success"
                else:
                    msg = "YouTube Error: " + (result.get("error") or "Unknown error")
                    msg_type = "error"
            except Exception as e:
                msg = "Error processing YouTube link: " + str(e)
                msg_type = "error"
        else:
            msg = "Please upload a video or provide a YouTube link."
            msg_type = "error"

    return render_template(
        template_name,
        summary=summary,
        output_video=output_video,
        caption_text=caption_text,
        caption_srt=caption_srt,
        narrated_summary=narrated_summary,
        narrated_video=narrated_video,
        smart_edit_summary=smart_edit_summary,
        smart_edit_video=smart_edit_video,
        youtube_summary=youtube_summary,
        youtube_transcript=youtube_transcript,
        youtube_title=youtube_title,
        msg=msg,
        msg_type=msg_type,
    )


if __name__ == "__main__":
    app.run(debug=True)
