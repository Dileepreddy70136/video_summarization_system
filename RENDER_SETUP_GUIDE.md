# Render Deployment Troubleshooting & Setup

## 🔧 Fixed Issues

### **1. Missing Gunicorn ✅**
- **Problem:** `gunicorn not found` during deployment
- **Solution:** Added `gunicorn==21.2.0` to `requirements.txt`
- **Status:** Fixed

### **2. Missing FFmpeg ✅**
- **Problem:** FFmpeg not available on Render
- **Solution:** Added `build.sh` to install system packages
- **Status:** Fixed

### **3. Worker Configuration ✅**
- **Problem:** Single worker timeout on large videos
- **Solution:** Increased to 2 workers with 120s timeout
- **Status:** Fixed

---

## **Correct Deployment Configuration**

### **Files in Place:**
- ✅ `Procfile` - `web: gunicorn app:app`
- ✅ `render.yaml` - Complete Render config
- ✅ `requirements.txt` - All dependencies including gunicorn
- ✅ `runtime.txt` - Python 3.11.0
- ✅ `build.sh` - System package installation script

### **Deployment Configuration:**

**Build Command:**
```bash
bash build.sh
```

**Start Command:**
```bash
gunicorn --workers 2 --timeout 120 app:app
```

**Environment Variables:**
```
PYTHON_VERSION=3.11.0
FLASK_ENV=production
PORT=5000
```

---

## **Step-by-Step Render Deployment**

### **1. Create Render Account**
- Visit: https://render.com
- Sign up with GitHub account

### **2. Connect Repository**
- Dashboard → New → Web Service
- Select: `video_summarization_system` repo
- Click "Connect"

### **3. Configure Service**

| Field | Value |
|-------|-------|
| **Name** | `video-summarizer` |
| **Environment** | Python 3 |
| **Build Command** | `bash build.sh` |
| **Start Command** | `gunicorn --workers 2 --timeout 120 app:app` |
| **Instance** | Free or Starter |
| **Region** | Oregon |

### **4. Environment Variables**
```
FLASK_ENV=production
PYTHON_VERSION=3.11.0
```

### **5. Deploy**
- Click "Create Web Service"
- Monitor logs for build progress
- Wait for "Your service is live" message

---

## **Build Process (What Happens)**

When you deploy to Render:

1. ✅ **System Setup** - Ubuntu Linux environment
2. ✅ **System Packages** - FFmpeg, libsndfile1 installed
3. ✅ **Python Environment** - Python 3.11.0 setup
4. ✅ **Dependencies** - All pip packages installed
5. ✅ **Verification** - Test imports (Flask, Torch, OpenCV)
6. ✅ **Start** - Gunicorn server starts with 2 workers

---

## **Common Deployment Errors & Fixes**

### **Error: `ModuleNotFoundError: No module named 'gunicorn'`**
- ✅ Fixed: Added to requirements.txt
- Deploy again!

### **Error: `ffmpeg not found`**
- ✅ Fixed: Added to build.sh
- Deploy again!

### **Error: `Timeout waiting for process to bind to port`**
- Solution: 
  - Increase timeout in start command (done: 120s)
  - Use fewer workers if needed
  - Check app startup time

### **Error: `Out of memory`**
- Solution:
  - Upgrade to Starter plan ($7/mo)
  - Reduce workers: `--workers 1`
  - Optimize model loading

### **Error: `Permission denied: 'build.sh'`**
- Solution:
  - File permissions automatically set by Render
  - No action needed

---

## **Testing Locally Before Deploy**

```bash
# Install gunicorn locally
pip install gunicorn

# Run with gunicorn (production mode)
gunicorn --workers 2 --timeout 120 app:app

# Should start on http://127.0.0.1:8000
# Access at: http://localhost:8000
```

---

## **After Deployment**

### **Success Indicators:**
- ✅ Status: "Live"
- ✅ URL: `https://video-summarizer.onrender.com`
- ✅ Logs show: "Application startup complete"
- ✅ Can access homepage

### **First Run:**
- First request may take 30-60 seconds (model loading)
- Subsequent requests faster (~5-10 seconds per video)

### **Monitor Logs:**
- Dashboard → Service → Logs
- Check for errors during video processing

---

## **Current Repository Status**

✅ Size: 9.02 MB (under 100 MB limit)  
✅ Dependencies: All specified  
✅ System packages: Auto-installed  
✅ Configuration: Complete  
✅ Ready to deploy!  

---

## **Deploy Now!**

1. Go to: https://render.com
2. New Web Service
3. Connect repo: `video_summarization_system`
4. Start command: `gunicorn --workers 2 --timeout 120 app:app`
5. Click Deploy!

Your app will be live in 2-5 minutes! 🚀

