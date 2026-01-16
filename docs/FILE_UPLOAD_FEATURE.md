# File Upload Feature

## Overview

The file upload feature allows users to upload audio files, PDFs, or text files for automatic transcription and summarization, without needing to record live.

## Supported File Types

### Audio Files

- **WAV** - Waveform Audio File Format
- **MP3** - MPEG Audio Layer 3
- **OGG** - Ogg Vorbis
- **FLAC** - Free Lossless Audio Codec
- **M4A** - MPEG-4 Audio
- **WEBM** - WebM Audio

### Text Files

- **PDF** - Portable Document Format
- **TXT** - Plain Text File

## Features

### Audio File Upload

1. Upload pre-recorded audio files
2. Automatic transcription using Vosk (offline)
3. Summary generation
4. PDF export for both transcript and summary
5. Audio playback in browser

### Text/PDF File Upload

1. Upload existing documents
2. Automatic text extraction
3. Summary generation
4. PDF export for both original text and summary

## How to Use

### From Dashboard

1. Click the **"Upload File"** button on the dashboard
2. Select file type (Audio or Text/PDF)
3. Enter a title for the recording
4. Click or drag-and-drop to select your file
5. Click **"Upload and Process"**
6. Wait for processing to complete
7. View results in the recording detail page

### Processing Time

- **Audio files**: Depends on file length (typically 1-5 minutes for a 10-minute audio)
- **Text/PDF files**: Usually under 30 seconds

## API Endpoints

### Upload Audio File

```
POST /api/upload/audio
Authorization: Bearer <token>
Content-Type: multipart/form-data

Body:
- file: Audio file
- title: Recording title (optional)

Response:
{
  "message": "Audio file uploaded and processed successfully",
  "recording_id": 123,
  "session_id": "upload_1_2024-01-16_12-30-00"
}
```

### Upload Text/PDF File

```
POST /api/upload/text
Authorization: Bearer <token>
Content-Type: multipart/form-data

Body:
- file: PDF or TXT file
- title: Recording title (optional)

Response:
{
  "message": "Text file uploaded and processed successfully",
  "recording_id": 124,
  "session_id": "upload_1_2024-01-16_12-35-00"
}
```

## Technical Details

### Backend Processing

#### Audio Files

1. File is saved to user-specific upload directory
2. Vosk STT engine transcribes the audio
3. Transcript is saved as text file
4. Summarizer generates summary
5. PDFs are created for both transcript and summary
6. Database record is updated with file paths

#### Text/PDF Files

1. File is saved to user-specific upload directory
2. Text is extracted (PyPDF2 for PDFs, direct read for TXT)
3. Transcript file is created with extracted text
4. Summarizer generates summary
5. PDFs are created for both transcript and summary
6. Database record is updated with file paths

### File Storage Structure

```
uploads/
└── user_<user_id>/
    └── <timestamp>_<filename>

iot-meeting-minutes/recordings/
└── user_<user_id>/
    └── upload_<user_id>_<timestamp>/
        ├── upload_<user_id>_<timestamp>.txt (transcript)
        └── upload_<user_id>_<timestamp>_summary.txt
```

## Limitations

- Maximum file size: 500 MB
- Audio must be mono (1 channel) for best results
- PDF text extraction may not work well with scanned images (OCR not included)
- Processing time increases with file size

## Error Handling

### Common Errors

**"Invalid file type"**

- Solution: Ensure file has correct extension and is one of the supported types

**"No text content extracted from file"**

- Solution: Check if PDF contains actual text (not just images)
- Solution: Ensure audio file is not corrupted

**"Transcription failed"**

- Solution: Check audio format (should be mono, 16kHz recommended)
- Solution: Ensure Vosk model is properly installed

**"Failed to upload file"**

- Solution: Check file size (must be under 500MB)
- Solution: Ensure you're logged in
- Solution: Check network connection

## Future Enhancements

- [ ] Support for stereo audio (automatic conversion to mono)
- [ ] OCR support for scanned PDFs
- [ ] Support for more audio formats (AAC, WMA)
- [ ] Batch upload (multiple files at once)
- [ ] Progress tracking for long transcriptions
- [ ] Speaker diarization (identify different speakers)
- [ ] Custom vocabulary for domain-specific terms

## Dependencies

### Backend

- `PyPDF2>=3.0.0` - PDF text extraction
- `vosk>=0.3.45` - Speech-to-text
- `wave` - Audio file handling (built-in)
- `werkzeug` - Secure filename handling

### Frontend

- React file upload with drag-and-drop
- Progress bar for upload tracking
- File type validation

## Security Considerations

- Files are stored in user-specific directories
- Filenames are sanitized using `secure_filename()`
- JWT authentication required for all upload endpoints
- File type validation on both frontend and backend
- Maximum file size limit enforced

## Testing

### Test Audio Upload

```bash
cd tests
python test_audio_upload.py
```

### Test Text Upload

```bash
cd tests
python test_text_upload.py
```

### Manual Testing

1. Prepare test files (audio, PDF, TXT)
2. Login to the application
3. Navigate to Upload page
4. Test each file type
5. Verify transcription/extraction accuracy
6. Check PDF generation
7. Test error cases (invalid files, large files)
