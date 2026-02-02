import sys
import os

# Ensure project root is in path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from summarizer.youtube_simple import summarize_youtube_simple
import json

url = "https://youtu.be/5WxSMovdT-U?si=DeeT36kk_Fxl8q8G"
result = summarize_youtube_simple(url)

if result['success']:
    print(result['summary'])
else:
    print(f"ERROR: {result['error']}")
