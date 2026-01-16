# Quick Reference Guide

## 🚀 Getting Started

### First Time Setup

```bash
# Run the setup script
setup.bat

# Or manually:
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

cd ../frontend
npm install
```

### Start Application

```bash
# Terminal 1 - Backend
cd backend
venv\Scripts\activate
python app.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### Access Application

- Frontend: http://localhost:5173
- Backend API: http://localhost:5000

---

## 📋 Features Overview

### 1. Live Recording

- Click "New Recording" on dashboard
- Speak into microphone
- Real-time transcription appears
- Click "Stop Recording" when done
- View transcript and summary

### 2. File Upload

- Click "Upload File" on dashboard
- Choose file type (Audio or Text/PDF)
- Select file
- Enter title
- Upload and wait for processing

### 3. View Recordings

- Dashboard shows all recordings
- Click on recording to view details
- Download PDFs
- Play audio (for recorded/uploaded audio)
- Delete recordings

---

## 📁 Supported File Types

### Audio Files (for transcription)

- WAV
- MP3
- OGG
- FLAC
- M4A
- WEBM

### Text Files (for summarization)

- PDF
- TXT

---

## 🔧 Configuration

### Vosk Model Path

Edit: `iot-meeting-minutes/configs/recorder_config.yml`

```yaml
model_path: K:\IOT\Iot-Meeting-Transcriber\models\vosk-model-small-en-in-0.4
```

### Summarization Mode

Edit: `iot-meeting-minutes/configs/recorder_config.yml`

```yaml
summarizer: textrank # or 't5_small' for better quality (slower)
extractive_sentences: 5 # number of sentences in summary
```

### Database Location

Edit: `backend/app.py` (line 48)

```python
db_path = os.path.join(os.path.dirname(__file__), "..", "data", "meeting_transcriber.db")
```

---

## 🛠️ Common Tasks

### Install New Python Package

```bash
cd backend
venv\Scripts\activate
pip install <package_name>
pip freeze > requirements.txt
```

### Install New Node Package

```bash
cd frontend
npm install <package_name>
```

### Reset Database

```bash
# Delete database file
del data\meeting_transcriber.db

# Restart backend (will recreate database)
cd backend
python app.py
```

### Clear Uploads

```bash
# Delete all uploaded files
rmdir /s /q backend\uploads
mkdir backend\uploads
```

### Clear Recordings

```bash
# Delete all recordings
rmdir /s /q iot-meeting-minutes\recordings
mkdir iot-meeting-minutes\recordings
```

---

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check Python version
python --version  # Should be 3.7+

# Reinstall dependencies
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend won't start

```bash
# Check Node version
node --version  # Should be 16+

# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### No microphone detected

- Check system microphone permissions
- Ensure microphone is connected
- Try different USB port
- Restart application

### Transcription not working

- Verify Vosk model path in config
- Check model file exists
- Ensure audio is mono (1 channel)
- Check microphone is working in other apps

### Upload fails

- Check file size (max 500MB)
- Verify file type is supported
- Ensure you're logged in
- Check network connection

### PDF generation fails

```bash
# Reinstall reportlab
cd backend
venv\Scripts\activate
pip install --upgrade reportlab
```

---

## 📊 API Endpoints Quick Reference

### Authentication

```
POST /api/auth/register    - Register new user
POST /api/auth/login       - Login user
GET  /api/auth/me          - Get current user
```

### Recordings

```
POST   /api/recordings/start                    - Start recording
POST   /api/recordings/<id>/stop                - Stop recording
GET    /api/recordings/<id>/transcript          - Get transcript
GET    /api/recordings                          - List recordings
GET    /api/recordings/<id>                     - Get recording details
DELETE /api/recordings/<id>                     - Delete recording
```

### File Upload

```
POST /api/upload/audio     - Upload audio file
POST /api/upload/text      - Upload text/PDF file
```

### PDFs

```
GET /api/recordings/<id>/pdf/transcript  - Download transcript PDF
GET /api/recordings/<id>/pdf/summary     - Download summary PDF
```

### Audio

```
GET /api/recordings/<id>/audio           - Stream audio file
```

---

## 📚 Documentation

- **README.md** - Main project documentation
- **docs/QUICKSTART.md** - Quick start guide
- **docs/TROUBLESHOOTING.md** - Troubleshooting guide
- **docs/FILE_UPLOAD_FEATURE.md** - File upload feature details
- **docs/UPLOAD_FLOW.md** - Upload flow diagrams
- **CHANGELOG.md** - Version history

---

## 🔐 Security Notes

### Production Deployment

1. Change SECRET_KEY and JWT_SECRET_KEY
2. Use environment variables for secrets
3. Use PostgreSQL instead of SQLite
4. Add rate limiting
5. Enable HTTPS
6. Set proper CORS origins

### Environment Variables

Create `.env` file in backend:

```env
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

---

## 📞 Support

For issues and questions:

1. Check documentation in `docs/` folder
2. Review troubleshooting guide
3. Check error logs in terminal
4. Verify configuration files

---

## 🎯 Quick Commands

```bash
# Start everything
setup.bat

# Backend only
cd backend && venv\Scripts\activate && python app.py

# Frontend only
cd frontend && npm run dev

# Install dependencies
cd backend && pip install -r requirements.txt
cd frontend && npm install

# Run tests
cd tests && python test_mic.py
cd tests && python test_vosk.py

# Build frontend for production
cd frontend && npm run build

# Check Python packages
cd backend && venv\Scripts\activate && pip list

# Check Node packages
cd frontend && npm list
```
