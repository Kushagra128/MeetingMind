"""
File Upload Service
Handles audio, PDF, and text file uploads for transcription and summarization
"""

import os
import sys
import wave
import json
from datetime import datetime
from pathlib import Path
import PyPDF2
from werkzeug.utils import secure_filename

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'iot-meeting-minutes'))

from vosk import Model, KaldiRecognizer
from summarizer import Summarizer
from database import db, Recording


class FileUploadService:
    def __init__(self, upload_folder, config):
        """Initialize file upload service"""
        self.upload_folder = upload_folder
        self.config = config
        self.allowed_audio_extensions = {'wav', 'mp3', 'ogg', 'flac', 'm4a', 'webm'}
        self.allowed_text_extensions = {'txt', 'pdf'}
        self.summarizer = Summarizer(
            config.get('summarizer', 'textrank'),
            config.get('extractive_sentences', 5)
        )
        
        # Load Vosk model for audio transcription
        try:
            self.vosk_model = Model(config['model_path'])
            print(f"[FileUploadService] Vosk model loaded from {config['model_path']}")
        except Exception as e:
            print(f"[FileUploadService] Warning: Could not load Vosk model: {e}")
            self.vosk_model = None
    
    def allowed_file(self, filename, file_type='audio'):
        """Check if file extension is allowed"""
        if '.' not in filename:
            return False
        
        ext = filename.rsplit('.', 1)[1].lower()
        
        if file_type == 'audio':
            return ext in self.allowed_audio_extensions
        elif file_type == 'text':
            return ext in self.allowed_text_extensions
        
        return False
    
    def save_uploaded_file(self, file, user_id):
        """Save uploaded file to disk"""
        if not file or file.filename == '':
            raise ValueError("No file provided")
        
        # Create user-specific upload directory
        user_upload_dir = os.path.join(self.upload_folder, f'user_{user_id}')
        os.makedirs(user_upload_dir, exist_ok=True)
        
        # Secure filename and add timestamp
        original_filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{original_filename}"
        
        file_path = os.path.join(user_upload_dir, filename)
        file.save(file_path)
        
        return file_path, original_filename
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF file"""
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def extract_text_from_txt(self, txt_path):
        """Extract text from TXT file"""
        try:
            with open(txt_path, 'r', encoding='utf-8') as file:
                text = file.read()
            return text.strip()
        except Exception as e:
            raise Exception(f"Failed to read text file: {str(e)}")
    
    def transcribe_audio_file(self, audio_path):
        """Transcribe audio file using Vosk"""
        if not self.vosk_model:
            raise Exception("Vosk model not loaded")
        
        try:
            # Open audio file
            wf = wave.open(audio_path, "rb")
            
            # Check audio format
            if wf.getnchannels() != 1:
                raise Exception("Audio must be mono (1 channel)")
            
            sample_rate = wf.getframerate()
            
            # Create recognizer
            recognizer = KaldiRecognizer(self.vosk_model, sample_rate)
            recognizer.SetWords(True)
            
            # Process audio
            transcript_segments = []
            full_text = ""
            
            print(f"[FileUploadService] Starting transcription of {audio_path}")
            
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    if result.get('text'):
                        segment_text = result['text']
                        full_text += segment_text + " "
                        transcript_segments.append({
                            'text': segment_text,
                            'words': result.get('result', [])
                        })
                        print(f"[Transcription] {segment_text}")
            
            # Get final result
            final_result = json.loads(recognizer.FinalResult())
            if final_result.get('text'):
                segment_text = final_result['text']
                full_text += segment_text
                transcript_segments.append({
                    'text': segment_text,
                    'words': final_result.get('result', [])
                })
                print(f"[Transcription] {segment_text}")
            
            wf.close()
            
            return {
                'full_text': full_text.strip(),
                'segments': transcript_segments
            }
            
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")
    
    def process_uploaded_file(self, file_path, file_type, original_filename, user_id, title):
        """Process uploaded file and create recording entry"""
        try:
            session_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            session_id = f"upload_{user_id}_{session_timestamp}"
            
            # Create recording entry
            recording = Recording(
                user_id=user_id,
                session_id=session_id,
                title=title or original_filename,
                status='processing'
            )
            db.session.add(recording)
            db.session.commit()
            
            transcript_text = ""
            
            # Process based on file type
            if file_type == 'audio':
                print(f"[FileUploadService] Processing audio file: {original_filename}")
                transcription_result = self.transcribe_audio_file(file_path)
                transcript_text = transcription_result['full_text']
                
                # Save audio file path
                recording.audio_file_path = file_path
                
            elif file_type == 'pdf':
                print(f"[FileUploadService] Processing PDF file: {original_filename}")
                transcript_text = self.extract_text_from_pdf(file_path)
                
            elif file_type == 'txt':
                print(f"[FileUploadService] Processing text file: {original_filename}")
                transcript_text = self.extract_text_from_txt(file_path)
            
            if not transcript_text or len(transcript_text.strip()) < 10:
                recording.status = 'failed'
                db.session.commit()
                raise Exception("No text content extracted from file")
            
            # Save transcript to file
            transcript_file = self._save_transcript(transcript_text, session_id, user_id)
            recording.transcript_file_path = transcript_file
            
            # Generate summary
            print(f"[FileUploadService] Generating summary...")
            summary = self.summarizer.generate_summary(transcript_text)
            summary_file = self.summarizer.save_summary(
                summary,
                os.path.dirname(transcript_file),
                session_id
            )
            recording.summary_file_path = summary_file
            
            # Update recording status
            recording.status = 'completed'
            db.session.commit()
            
            return {
                'recording_id': recording.id,
                'session_id': session_id,
                'transcript_file': transcript_file,
                'summary_file': summary_file,
                'transcript_text': transcript_text,
                'summary_text': summary
            }
            
        except Exception as e:
            print(f"[FileUploadService] Error processing file: {e}")
            if recording:
                recording.status = 'failed'
                db.session.commit()
            raise
    
    def _save_transcript(self, text, session_id, user_id):
        """Save transcript to file"""
        # Create session folder
        user_recordings_dir = os.path.join(
            os.path.dirname(__file__),
            '..',
            'iot-meeting-minutes',
            'recordings',
            f'user_{user_id}'
        )
        os.makedirs(user_recordings_dir, exist_ok=True)
        
        session_folder = os.path.join(user_recordings_dir, session_id)
        os.makedirs(session_folder, exist_ok=True)
        
        # Save transcript
        transcript_file = os.path.join(session_folder, f"{session_id}.txt")
        
        with open(transcript_file, 'w', encoding='utf-8') as f:
            f.write(f"Transcript: {session_id}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            f.write(text)
            f.write("\n\n" + "=" * 60 + "\n")
        
        return transcript_file
    
    def delete_uploaded_file(self, file_path):
        """Delete uploaded file from disk"""
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                print(f"[FileUploadService] Deleted file: {file_path}")
        except Exception as e:
            print(f"[FileUploadService] Error deleting file: {e}")
