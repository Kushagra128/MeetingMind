# Quick Start Guide

## Step 1: Install Backend Dependencies

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

## Step 2: Install Frontend Dependencies

```bash
cd frontend
npm install
```

## Step 3: Configure Vosk Model

1. Ensure you have a Vosk model in the project directory
2. Update `iot-meeting-minutes/configs/recorder_config.yml` with the correct model path

## Step 4: Start Backend

```bash
cd backend
python app.py
```

Backend runs on: http://localhost:5000

## Step 5: Start Frontend

In a new terminal:

```bash
cd frontend
npm run dev
```

Frontend runs on: http://localhost:5173

## Step 6: Use the Application

1. Open http://localhost:5173 in your browser
2. Register a new account
3. Click "New Recording" to start recording
4. Speak into your microphone
5. Click "Stop Recording" when done
6. View transcript and summary
7. Download PDFs

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (needs 3.7+)
- Ensure virtual environment is activated
- Install dependencies: `pip install -r requirements.txt`

### Frontend won't start
- Check Node version: `node --version` (needs 16+)
- Install dependencies: `npm install`

### No microphone detected
- Check system microphone permissions
- Ensure microphone is connected
- Try restarting the application

### Transcription not working
- Verify Vosk model path in config
- Check model file exists
- Ensure microphone is working in other apps



