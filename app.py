from flask import Flask, abort, render_template, request, send_from_directory
from summarizer.video_summarizer import summarize_video
from summarizer.auto_caption import transcribe_video
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
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


@app.route("/", methods=["GET", "POST"])
def index():
    # Video flow
    summary = ""
    output_video = ""
    caption_text = ""
    caption_srt = ""
    # Common
    msg = ""
    msg_type = "success"  # success | error

    if request.method == "POST":
        video_file = request.files.get("video_file")
        do_summary = request.form.get("do_summary") == "on"
        do_caption = request.form.get("do_caption") == "on"

        # ---- Video: summarize and/or auto-caption ----
        if video_file and video_file.filename:
            if not do_summary and not do_caption:
                msg = "Please select at least one: Summarize video or Auto captions."
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

                    if msg_type != "error" and not msg:
                        msg = "Video processed successfully!"
                        msg_type = "success"

                except Exception as e:
                    msg = "Error processing video: " + str(e)
                    msg_type = "error"
        else:
            msg = "Please upload a video."
            msg_type = "error"

    return render_template(
        "index.html",
        summary=summary,
        output_video=output_video,
        caption_text=caption_text,
        caption_srt=caption_srt,
        msg=msg,
        msg_type=msg_type,
    )


if __name__ == "__main__":
    app.run(debug=True)
