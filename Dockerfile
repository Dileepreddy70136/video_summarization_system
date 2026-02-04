FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements-render.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create output directories
RUN mkdir -p output/audio output/video uploads/temp_audio

# Expose port
EXPOSE 5000

# Run with gunicorn
CMD ["gunicorn", "--workers", "2", "--timeout", "120", "--bind", "0.0.0.0:5000", "app:app"]
