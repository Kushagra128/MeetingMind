"""
Recording Service
Manages recording sessions and integrates with the existing transcription system
"""

import os
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
import json
import wave
import yaml

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'iot-meeting-minutes'))

from recorder import AudioRecorder
from stt_engine import VoskSTTEngine
from transcript_aggregator import TranscriptAggregator
from summarizer import Summarizer
from logger import SessionLogger

from database import db, Recording


class RecordingService:
    def __init__(self):
        """Initialize recording service"""
        self.active_sessions = {}  # session_id -> session_data
        self.config = self._load_config()
        
    def _load_config(self):
        """Load configuration"""
        config_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'iot-meeting-minutes',
            'configs',
            'recorder_config.yml'
        )
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        else:
            # Default config
            return {
                'model_path': os.path.join(
                    os.path.dirname(__file__),
                    '..',
                    'vosk-model-small-en-in-0.4'
                ),
                'sample_rate': 16000,
                'channels': 1,
                'block_duration_ms': 500,
                'save_dir': 'recordings',
                'summarizer': 'textrank',
                'extractive_sentences': 5
            }
    
    def start_session(self, user_id, title):
        """Start a new recording session"""
        session_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        session_id = f"session_{user_id}_{session_timestamp}"
        
        # Create user-specific recording directory
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
        
        # Create database record
        recording = Recording(
            user_id=user_id,
            session_id=session_id,
            title=title,
            status='recording'
        )
        db.session.add(recording)
        db.session.commit()
        
        try:
            # Initialize components
            recorder = AudioRecorder(
                self.config,
                session_folder,
                session_id
            )
            
            stt_engine = VoskSTTEngine(
                self.config['model_path'],
                self.config['sample_rate']
            )
            
            aggregator = TranscriptAggregator(
                session_folder,
                session_id
            )
            
            summarizer = Summarizer(
                self.config['summarizer'],
                self.config['extractive_sentences']
            )
            
            logger = SessionLogger(session_folder, session_id)
            
            # Start recording
            recorder.start()
            
            # Store session data
            self.active_sessions[session_id] = {
                'user_id': user_id,
                'recording_id': recording.id,
                'session_folder': session_folder,
                'session_name': session_id,
                'recorder': recorder,
                'stt_engine': stt_engine,
                'aggregator': aggregator,
                'summarizer': summarizer,
                'logger': logger,
                'start_time': time.time(),
                'running': True,
                'transcript': []
            }
            
            # Start processing thread
            processing_thread = threading.Thread(
                target=self._process_audio_stream,
                args=(session_id,),
                daemon=True
            )
            processing_thread.start()
            
            return session_id
            
        except Exception as e:
            # Update status to failed
            recording.status = 'failed'
            db.session.commit()
            raise Exception(f"Failed to start recording: {str(e)}")
    
    def _process_audio_stream(self, session_id):
        """Process audio stream in background thread"""
        session = self.active_sessions.get(session_id)
        if not session:
            return
        
        try:
            while session['running']:
                # Get audio block
                audio_block = session['recorder'].get_audio_block(timeout=0.1)
                
                if audio_block is None:
                    continue
                
                # Process with STT
                result = session['stt_engine'].process_audio(audio_block)
                
                if result:
                    if result['type'] == 'partial':
                        # Just for debugging – you can comment this if noisy
                        print(f"[STT][partial] {result['text']}")
                        
                        # Update partial results for real-time display
                        if session['transcript']:
                            last_item = session['transcript'][-1]
                            if last_item.get('type') == 'partial':
                                last_item['text'] = result['text']
                            else:
                                session['transcript'].append({
                                    'text': result['text'],
                                    'timestamp': datetime.now().isoformat(),
                                    'type': 'partial'
                                })
                        else:
                            session['transcript'].append({
                                'text': result['text'],
                                'timestamp': datetime.now().isoformat(),
                                'type': 'partial'
                            })
                    elif result['type'] == 'final':
                        print(f"[STT][final] {result['text']}")
                        # Add to transcript
                        session['aggregator'].add_segment(result['text'], result.get('words'))
                        # Remove any matching partial and add final
                        session['transcript'] = [
                            t for t in session['transcript']
                            if not (t.get('type') == 'partial' and t.get('text') == result['text'])
                        ]
                        session['transcript'].append({
                            'text': result['text'],
                            'timestamp': datetime.now().isoformat(),
                            'type': 'final'
                        })
                        session['logger'].log(f"Transcribed: {result['text'][:50]}...")
                
        except Exception as e:
            print(f"[RecordingService] Error during streaming STT: {e}")
            session['logger'].log(f"Error during processing: {e}", level="ERROR")
    
    def _offline_transcribe_from_wav(self, session):
        """
        Fallback: run Vosk on the saved WAV file if streaming
        transcription produced nothing.
        """
        wav_path = os.path.join(
            session['session_folder'],
            f"{session['session_name']}.wav"
        )
        
        if not os.path.exists(wav_path):
            print(f"[RecordingService] WAV file not found for offline transcription: {wav_path}")
            return
        
        print(f"[RecordingService] Running offline transcription on {wav_path} ...")
        
        try:
            wf = wave.open(wav_path, "rb")
            
            # Sanity check – Vosk expects mono 16k 16-bit, but will usually cope if close
            from vosk import KaldiRecognizer
            recognizer = KaldiRecognizer(session['stt_engine'].model, wf.getframerate())
            
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if recognizer.AcceptWaveform(data):
                    res = json.loads(recognizer.Result())
                    if res.get('text'):
                        session['aggregator'].add_segment(res['text'], res.get('result', []))
                        print(f"[STT][offline-final] {res['text']}")
            
            final = json.loads(recognizer.FinalResult())
            if final.get('text'):
                session['aggregator'].add_segment(final['text'], final.get('result', []))
                print(f"[STT][offline-final] {final['text']}")
            
        except Exception as e:
            print(f"[RecordingService] Offline transcription failed: {e}")
    
    def stop_session(self, session_id, user_id):
        """Stop recording session and process"""
        if session_id not in self.active_sessions:
            print(f"Warning: Session {session_id} not found or already stopped")
            return None
        
        session = self.active_sessions.get(session_id)
        
        if not session or session['user_id'] != user_id:
            return None
        
        # Mark as stopping to prevent duplicate calls
        if not session.get('running', True):
            print(f"Warning: Session {session_id} already stopped")
            return None
        
        try:
            session['running'] = False
            
            # Stop recorder
            session['recorder'].stop()
            
            # Try to get final streaming result
            try:
                final_result = session['stt_engine'].get_final_result()
                if final_result and final_result.get('text'):
                    print(f"[STT][stream-final] {final_result['text']}")
                    session['aggregator'].add_segment(final_result['text'], final_result.get('words'))
            except Exception as e:
                print(f"Warning: Could not get final STT result: {e}")
                session['logger'].log(f"Warning: Could not get final STT result: {e}", level="WARNING")
            
            # If still no transcript, run offline transcription on WAV
            transcript_text = session['aggregator'].get_full_transcript()
            if not transcript_text.strip():
                print("[RecordingService] No transcript text detected from streaming STT – trying offline transcription from WAV...")
                self._offline_transcribe_from_wav(session)
                transcript_text = session['aggregator'].get_full_transcript()
                if not transcript_text.strip():
                    print("[RecordingService] Offline transcription also produced no text.")
            
            # Save transcript (whatever we have)
            transcript_file = session['aggregator'].save_transcript()
            
            # Generate summary
            transcript_text = session['aggregator'].get_full_transcript()
            summary = None
            summary_file = None
            
            if transcript_text.strip():
                summary = session['summarizer'].generate_summary(transcript_text)
                summary_file = session['summarizer'].save_summary(
                    summary,
                    session['session_folder'],
                    session['session_name']
                )
            else:
                print("[RecordingService] Transcript still empty – skipping summary generation.")
            
            # Save metadata
            duration = time.time() - session['start_time']
            self._save_metadata(session, duration)
            
            # Close logger
            session['logger'].close()
            
            # Update database
            recording = Recording.query.filter_by(id=session['recording_id']).first()
            if recording:
                recording.status = 'completed'
                recording.duration = duration
                recording.audio_file_path = os.path.join(
                    session['session_folder'],
                    f"{session['session_name']}.wav"
                )
                recording.transcript_file_path = transcript_file
                recording.summary_file_path = summary_file
                recording.metadata_file_path = os.path.join(
                    session['session_folder'],
                    f"{session['session_name']}_meta.json"
                )
                db.session.commit()
            
            # Build result before removing from active sessions
            result = {
                'session_id': session_id,
                'session_name': session['session_name'],
                'transcript_file': transcript_file,
                'summary_file': summary_file,
                'duration': duration
            }
            
            # Remove from active sessions
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            return result
            
        except Exception as e:
            # Update status to failed
            recording = Recording.query.filter_by(id=session['recording_id']).first()
            if recording:
                recording.status = 'failed'
                db.session.commit()
            
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            raise Exception(f"Failed to stop recording: {str(e)}")
    
    def _save_metadata(self, session, duration):
        """Save session metadata"""
        meta_file = os.path.join(
            session['session_folder'],
            f"{session['session_name']}_meta.json"
        )
        
        metadata = {
            'session_name': session['session_name'],
            'user_id': session['user_id'],
            'start_time': datetime.fromtimestamp(session['start_time']).isoformat(),
            'stop_time': datetime.now().isoformat(),
            'duration': duration,
            'sample_rate': self.config['sample_rate'],
            'channels': self.config['channels'],
            'vosk_model_path': self.config['model_path'],
            'wav_file': f"{session['session_name']}.wav",
            'transcript_file': f"{session['session_name']}.txt",
            'summary_file': f"{session['session_name']}_summary.txt",
            'summary_mode': self.config['summarizer']
        }
        
        with open(meta_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def get_transcript(self, session_id, user_id):
        """Get current transcript for a session"""
        session = self.active_sessions.get(session_id)
        
        if not session or session['user_id'] != user_id:
            return None
        
        # Get full transcript
        full_text = session['aggregator'].get_full_transcript()
        timestamped = session['aggregator'].get_timestamped_transcript()
        
        return {
            'full_text': full_text,
            'segments': timestamped,
            'word_count': session['aggregator'].get_word_count(),
            'segment_count': session['aggregator'].get_segment_count()
        }
    
    def delete_recording_files(self, recording):
        """Delete all files associated with a recording"""
        try:
            files_to_delete = [
                recording.audio_file_path,
                recording.transcript_file_path,
                recording.summary_file_path,
                recording.transcript_pdf_path,
                recording.summary_pdf_path,
                recording.metadata_file_path
            ]
            
            for file_path in files_to_delete:
                if file_path and os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Error deleting file {file_path}: {e}")
            
            # Try to delete session folder if empty
            if recording.audio_file_path:
                session_folder = os.path.dirname(recording.audio_file_path)
                try:
                    if os.path.exists(session_folder) and not os.listdir(session_folder):
                        os.rmdir(session_folder)
                except Exception:
                    pass  # Folder not empty or other error
        except Exception as e:
            print(f"Error deleting recording files: {e}")
