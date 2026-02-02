#!/bin/bash
set -e

echo "Building Video Summarization System for Render..."

# Install system dependencies
echo "Installing system packages..."
apt-get update
apt-get install -y ffmpeg libsndfile1 libgomp1

# Install Python dependencies
echo "Installing Python packages..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Verify installation
echo "Verifying installation..."
python -c "import flask; import torch; import cv2; print('✓ All dependencies installed')"

echo "Build complete!"
