# Meeting Transcriber

A full-stack web application for recording meetings, transcribing them using offline speech-to-text (Vosk), and generating intelligent summaries.

## 🚀 Features

- ✅ **User Authentication** - Secure JWT-based registration and login
- 🎤 **Real-time Recording** - Record meetings with live transcription
- 📤 **File Upload** - Upload audio files (WAV, MP3, OGG, FLAC, M4A) or text files (PDF, TXT) for processing
- 📝 **Offline Transcription** - Uses Vosk for privacy-focused, offline speech-to-text
- 📊 **Smart Summarization** - Automatic summary generation (TextRank or T5)
- 📄 **PDF Export** - Download transcripts and summaries as PDFs
- 💾 **User Spaces** - Each user has their own recording library
- 🗄️ **SQLite Database** - Lightweight database for user and recording management
- 🎧 **Audio Playback** - Listen to recordings directly in the browser

## 📁 Project Structure

```
Iot-Meeting-Transcriber/
├── backend/                    # Flask REST API
│   ├── app.py                 # Main Flask application
│   ├── database.py            # SQLAlchemy models
│   ├── recording_service.py   # Recording session management
│   ├── pdf_generator.py       # PDF generation service
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # React + Vite frontend
│   ├── src/
│   │   ├── pages/            # Page components
│   │   ├── components/       # Reusable components
│   │   └── contexts/         # React contexts (Auth)
│   └── package.json          # Node dependencies
│
├── iot-meeting-minutes/       # Core transcription engine
│   ├── recorder.py           # Audio recording (PyAudio)
│   ├── stt_engine.py         # Vosk STT engine
│   ├── summarizer.py         # Text summarization
│   ├── transcript_aggregator.py
│   └── configs/              # Configuration files
│
├── models/                    # Vosk speech recognition models
│   └── vosk-model-small-en-in-0.4/
│
├── data/                      # Application data
│   └── meeting_transcriber.db # SQLite database
│
├── tests/                     # Test files
├── experiments/               # Experimental/prototype code
└── docs/                      # Documentation
    ├── README.md             # Detailed documentation
    ├── QUICKSTART.md         # Quick start guide
    └── TROUBLESHOOTING.md    # Troubleshooting guide

```

## 🛠️ Prerequisites

- **Python 3.7+**
- **Node.js 16+** and npm
- **Microphone** (for recording)
- **Vosk Model** (download separately)

## 📦 Installation

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

### 3. Vosk Model Setup

The project includes a Vosk model in `models/vosk-model-small-en-in-0.4/`. If you need a different model:

1. Download from [https://alphacephei.com/vosk/models](https://alphacephei.com/vosk/models)
2. Extract to the `models/` directory
3. Update `iot-meeting-minutes/configs/recorder_config.yml` with the new path

**Recommended Models:**

- **Small (50MB)**: `vosk-model-small-en-us-0.15` - Fast, good accuracy
- **Medium (1.8GB)**: `vosk-model-en-us-0.22` - Better accuracy
- **Large (3GB)**: `vosk-model-en-us-0.22-lgraph` - Best accuracy

## 🚀 Running the Application

### Start Backend Server

```bash
cd backend
python app.py
```

Backend runs on: **http://localhost:5000**

### Start Frontend Development Server

```bash
cd frontend
npm run dev
```

Frontend runs on: **http://localhost:5173**

## 📖 Usage

### Live Recording

1. **Register/Login** - Create an account or login
2. **Start Recording** - Click "New Recording" button
3. **Record Meeting** - Speak into your microphone (transcription appears in real-time)
4. **Stop Recording** - Click "Stop Recording" when finished
5. **View Results** - View transcript and summary on the recording detail page
6. **Download PDFs** - Download or preview transcript and summary PDFs
7. **Manage Recordings** - View, play, or delete recordings from your dashboard

### File Upload

1. **Register/Login** - Create an account or login
2. **Upload File** - Click "Upload File" button on dashboard
3. **Select Type** - Choose Audio or Text/PDF
4. **Choose File** - Select your file (WAV, MP3, PDF, TXT, etc.)
5. **Add Title** - Enter a descriptive title
6. **Upload** - Click "Upload and Process"
7. **View Results** - Automatically redirected to results when processing completes

**Supported Formats:**

- **Audio**: WAV, MP3, OGG, FLAC, M4A, WEBM
- **Text**: PDF, TXT

3. **Record Meeting** - Speak into your microphone (transcription appears in real-time)
4. **Stop Recording** - Click "Stop Recording" when finished
5. **View Results** - View transcript and summary on the recording detail page
6. **Download PDFs** - Download or preview transcript and summary PDFs
7. **Manage Recordings** - View, play, or delete recordings from your dashboard

## 🔧 Configuration

### Backend Configuration

Edit `iot-meeting-minutes/configs/recorder_config.yml`:

```yaml
model_path: K:\IOT\Iot-Meeting-Transcriber\models\vosk-model-small-en-in-0.4
sample_rate: 16000
channels: 1
summarizer: textrank # or 't5_small' for abstractive summarization
extractive_sentences: 5
```

### Environment Variables (Optional)

Create a `.env` file in the backend directory:

```env
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
```

## 🔐 Security Notes

- Change `SECRET_KEY` and `JWT_SECRET_KEY` in production
- Use environment variables for sensitive configuration
- Consider PostgreSQL for production instead of SQLite
- Implement rate limiting for API endpoints
- Add HTTPS in production

## 📚 Documentation

- **[Detailed Documentation](docs/README.md)** - Complete feature documentation
- **[Quick Start Guide](docs/QUICKSTART.md)** - Get started in 5 minutes
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

## 🧪 Testing

Test files are located in the `tests/` directory:

```bash
# Test microphone
python tests/test_mic.py

# Test Vosk STT
python tests/test_vosk.py

# Test summarizer
python tests/test_summarizer.py

# Test JWT authentication
python tests/test_jwt.py
```

## 🏗️ Tech Stack

### Backend

- **Flask** - Web framework
- **SQLAlchemy** - ORM
- **Flask-JWT-Extended** - Authentication
- **Vosk** - Offline speech recognition
- **PyAudio** - Audio recording
- **ReportLab** - PDF generation
- **NLTK/scikit-learn** - Text summarization

### Frontend

- **React** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **React Router** - Navigation
- **Lucide React** - Icons

## 📄 License

This project is provided as-is for educational and personal use.

## 🙏 Credits

- [Vosk](https://alphacephei.com/vosk/) - Offline speech recognition
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [React](https://react.dev/) - Frontend framework
- [Tailwind CSS](https://tailwindcss.com/) - CSS framework

## 🐛 Troubleshooting

See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for common issues and solutions.

## 📞 Support

For issues and questions, please check the documentation in the `docs/` folder.
