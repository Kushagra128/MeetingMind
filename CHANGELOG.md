# Changelog

## [1.1.0] - 2024-01-16

### Added - File Upload Feature

#### New Functionality

- **Audio File Upload**: Upload pre-recorded audio files (WAV, MP3, OGG, FLAC, M4A, WEBM) for transcription
- **Text File Upload**: Upload PDF or TXT files for summarization
- **Automatic Processing**: Uploaded files are automatically transcribed/extracted and summarized
- **PDF Generation**: Both transcript and summary PDFs are generated for uploaded files

#### Backend Changes

- Added `file_upload_service.py` - New service for handling file uploads and processing
- Added `/api/upload/audio` endpoint - Upload and transcribe audio files
- Added `/api/upload/text` endpoint - Upload and summarize text/PDF files
- Added `PyPDF2` dependency for PDF text extraction
- Updated `app.py` to integrate file upload service
- Updated `requirements.txt` with new dependencies

#### Frontend Changes

- Added `Upload.jsx` - New upload page with drag-and-drop interface
- Updated `App.jsx` - Added `/upload` route
- Updated `Dashboard.jsx` - Added "Upload File" button
- File type selection (Audio vs Text/PDF)
- Upload progress tracking
- File validation and error handling

#### Documentation

- Added `docs/FILE_UPLOAD_FEATURE.md` - Comprehensive feature documentation
- Updated `README.md` - Added file upload feature to features list and usage guide
- Created `CHANGELOG.md` - Track project changes

#### Features

- Drag-and-drop file upload
- File type validation (frontend and backend)
- Progress bar during upload
- Automatic title suggestion from filename
- User-specific file storage
- Secure filename handling
- Maximum file size limit (500MB)

---

## [1.0.0] - Initial Release

### Features

- User authentication (JWT-based)
- Real-time audio recording
- Live transcription using Vosk
- Automatic summarization (TextRank/T5)
- PDF export for transcripts and summaries
- Audio playback
- User-specific recording spaces
- SQLite database
- React + Vite frontend
- Flask backend
- Offline speech-to-text

### Project Structure

- Organized folder structure
- Backend (Flask API)
- Frontend (React + Vite)
- Core transcription engine
- Models directory for Vosk
- Data directory for database
- Tests directory
- Documentation
