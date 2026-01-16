# File Upload Flow Diagram

## Audio File Upload Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER ACTIONS                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Click "Upload   │
                    │  File" Button    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Select "Audio"  │
                    │  File Type       │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Choose Audio    │
                    │  File (WAV, MP3) │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Enter Title     │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Click "Upload   │
                    │  and Process"    │
                    └────────┬─────────┘
                             │
┌────────────────────────────┴────────────────────────────┐
│                    BACKEND PROCESSING                    │
└──────────────────────────────────────────────────────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Save File to    │
                    │  User Directory  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Create Database │
                    │  Recording Entry │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Load Vosk Model │
                    │  & Initialize    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Transcribe      │
                    │  Audio File      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Save Transcript │
                    │  to Text File    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Generate        │
                    │  Summary         │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Save Summary    │
                    │  to Text File    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Generate        │
                    │  Transcript PDF  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Generate        │
                    │  Summary PDF     │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Update Database │
                    │  with File Paths │
                    └────────┬─────────┘
                             │
┌────────────────────────────┴────────────────────────────┐
│                    USER INTERFACE                        │
└──────────────────────────────────────────────────────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Redirect to     │
                    │  Recording Detail│
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Display:        │
                    │  - Transcript    │
                    │  - Summary       │
                    │  - Download PDFs │
                    │  - Play Audio    │
                    └──────────────────┘
```

## Text/PDF File Upload Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER ACTIONS                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Click "Upload   │
                    │  File" Button    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Select "Text/   │
                    │  PDF" File Type  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Choose File     │
                    │  (PDF or TXT)    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Enter Title     │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Click "Upload   │
                    │  and Process"    │
                    └────────┬─────────┘
                             │
┌────────────────────────────┴────────────────────────────┐
│                    BACKEND PROCESSING                    │
└──────────────────────────────────────────────────────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Save File to    │
                    │  User Directory  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Create Database │
                    │  Recording Entry │
                    └────────┬─────────┘
                             │
                             ▼
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
        ┌──────────────┐      ┌──────────────┐
        │  Extract     │      │  Read Text   │
        │  Text from   │      │  from TXT    │
        │  PDF         │      │  File        │
        └──────┬───────┘      └──────┬───────┘
               │                     │
               └──────────┬──────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │  Save Extracted  │
                 │  Text as         │
                 │  Transcript File │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │  Generate        │
                 │  Summary         │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │  Save Summary    │
                 │  to Text File    │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │  Generate        │
                 │  Transcript PDF  │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │  Generate        │
                 │  Summary PDF     │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │  Update Database │
                 │  with File Paths │
                 └────────┬─────────┘
                          │
┌─────────────────────────┴────────────────────────────┐
│                    USER INTERFACE                     │
└───────────────────────────────────────────────────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │  Redirect to     │
                 │  Recording Detail│
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │  Display:        │
                 │  - Transcript    │
                 │  - Summary       │
                 │  - Download PDFs │
                 └──────────────────┘
```

## File Storage Structure

```
Iot-Meeting-Transcriber/
│
├── backend/
│   └── uploads/                          # Uploaded files
│       └── user_<user_id>/
│           └── <timestamp>_<filename>    # Original uploaded file
│
└── iot-meeting-minutes/
    └── recordings/                       # Processed files
        └── user_<user_id>/
            └── upload_<user_id>_<timestamp>/
                ├── upload_<user_id>_<timestamp>.txt           # Transcript
                ├── upload_<user_id>_<timestamp>_summary.txt   # Summary
                ├── upload_<user_id>_<timestamp>_transcript.pdf
                └── upload_<user_id>_<timestamp>_summary.pdf
```

## API Endpoints

### Upload Audio

```
POST /api/upload/audio
Authorization: Bearer <JWT_TOKEN>
Content-Type: multipart/form-data

Request Body:
- file: <audio_file>
- title: "Meeting Recording"

Response (201):
{
  "message": "Audio file uploaded and processed successfully",
  "recording_id": 123,
  "session_id": "upload_1_2024-01-16_12-30-00"
}
```

### Upload Text/PDF

```
POST /api/upload/text
Authorization: Bearer <JWT_TOKEN>
Content-Type: multipart/form-data

Request Body:
- file: <pdf_or_txt_file>
- title: "Meeting Notes"

Response (201):
{
  "message": "Text file uploaded and processed successfully",
  "recording_id": 124,
  "session_id": "upload_1_2024-01-16_12-35-00"
}
```

## Error Handling

```
┌──────────────────┐
│  File Upload     │
└────────┬─────────┘
         │
         ▼
    ┌────────┐
    │ Valid? │──No──▶ Return 400: "Invalid file type"
    └───┬────┘
        │ Yes
        ▼
    ┌────────┐
    │ Size?  │──Too Large──▶ Return 400: "File too large"
    └───┬────┘
        │ OK
        ▼
    ┌────────┐
    │Process │──Error──▶ Return 500: "Processing failed"
    └───┬────┘
        │ Success
        ▼
    ┌────────┐
    │ Return │
    │  201   │
    └────────┘
```
