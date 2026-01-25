# Using FFmpeg with Video Summarization

The app uses **FFmpeg** to convert summarized videos to H.264 so they play in Chrome, Edge, and Firefox.

## Your `ffmpeg-8.0.1` folder

The `ffmpeg-8.0.1` folder in Downloads is the **source code**—it does not include `ffmpeg.exe`. You need a **Windows build**.

## Option A – Essentials build (recommended)

1. Download: [ffmpeg-release-essentials.zip](https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip)
2. Extract the ZIP.
3. Use one of these:

   **A1 – Use the extracted folder as-is**  
   The app will auto-detect:
   - `%USERPROFILE%\Downloads\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe`

   **A2 – Use your existing `ffmpeg-8.0.1` folder**  
   - Create `bin` inside `Downloads\ffmpeg-8.0.1\`
   - Copy `ffmpeg.exe` from the essentials build’s `bin` folder into `Downloads\ffmpeg-8.0.1\bin\`  
   The app will auto-detect:
   - `%USERPROFILE%\Downloads\ffmpeg-8.0.1\bin\ffmpeg.exe`

## Option B – Add FFmpeg to PATH

1. Get a Windows build (e.g. essentials or full from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/)).
2. Extract it and add the `bin` folder to your system **PATH**.

## Option C – Set the path manually

Set one of these before running the app:

- **Full path to the executable:**
  ```
  set FFMPEG_PATH=C:\Users\DileepReddy\Downloads\ffmpeg-8.0.1\bin\ffmpeg.exe
  ```
- **Folder that contains `ffmpeg.exe`:**
  ```
  set FFMPEG_BIN=C:\Users\DileepReddy\Downloads\ffmpeg-8.0.1\bin
  ```

In PowerShell:
```powershell
$env:FFMPEG_PATH = "C:\Users\DileepReddy\Downloads\ffmpeg-8.0.1\bin\ffmpeg.exe"
python app.py
```

## Check that it works

After placing `ffmpeg.exe` and starting the app, run **Process Video** with **Summarize video** checked. The resulting `summary_video.mp4` should play in the browser.
