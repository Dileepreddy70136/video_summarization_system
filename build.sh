#!/bin/bash
set -e

echo "Installing system dependencies for Video Summarization System..."

# Update package lists
apt-get update || true

# Install required system packages
apt-get install -y ffmpeg libsndfile1 libgomp1 || echo "Some packages may not be available"

# Upgrade Python tools
pip install --upgrade pip setuptools wheel

# Install Python dependencies
echo "Installing Python packages from requirements.txt..."
pip install -r requirements.txt

# Quick verification
echo "Verifying core packages..."
python -c "import flask; import torch; print('Build verification: OK')"

echo "Build completed successfully!"
