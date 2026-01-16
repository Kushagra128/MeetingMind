FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for PyAudio and audio processing
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    python3-pyaudio \
    gcc \
    g++ \
    make \
    libasound-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . .

# Copy iot-meeting-minutes module
COPY ../iot-meeting-minutes ./iot-meeting-minutes

# Copy models directory
COPY ../models ./models

# Create necessary directories
RUN mkdir -p uploads data

# Expose port
EXPOSE 5000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py

# Run the application
CMD ["python", "app.py"]
