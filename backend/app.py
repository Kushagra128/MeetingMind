"""
Flask Backend API for MeetingMing
Handles user authentication, recording sessions, and file management
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path to import modules from iot-meeting-minutes
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "iot-meeting-minutes"))

from database import db, User, Recording
from recording_service import RecordingService
from pdf_generator import PDFGenerator
from file_upload_service import FileUploadService
import yaml

# -----------------------------------------------------------------------------
# Flask & Config
# -----------------------------------------------------------------------------
app = Flask(__name__)

# Secrets (change in production or load from .env)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "your-secret-key-change-in-production"
)
app.config["JWT_SECRET_KEY"] = os.environ.get(
    "JWT_SECRET_KEY", "jwt-secret-key-change-in-production"
)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)

# Uploaded files
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "uploads")
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024  # 500 MB

# Database
db_path = os.path.join(os.path.dirname(__file__), "..", "data", "meeting_transcriber.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# -----------------------------------------------------------------------------
# Extensions
# -----------------------------------------------------------------------------
jwt = JWTManager(app)
db.init_app(app)

# CORS – allow your Vite dev frontend
CORS(
    app,
    origins=["http://localhost:5173", "http://localhost:3000"],
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
)

# Create tables on startup
with app.app_context():
    db.create_all()

# Load config for file upload service
config_path = os.path.join(
    os.path.dirname(__file__),
    '..',
    'iot-meeting-minutes',
    'configs',
    'recorder_config.yml'
)
with open(config_path, 'r') as f:
    upload_config = yaml.safe_load(f)

# Services
recording_service = RecordingService()
pdf_generator = PDFGenerator()
file_upload_service = FileUploadService(app.config["UPLOAD_FOLDER"], upload_config)

# Ensure upload folder exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def get_current_user_id():
    """
    Get current user ID from JWT token.
    We store identity as a string in the token, so convert to int.
    """
    user_id_str = get_jwt_identity()
    if not user_id_str:
        return None
    try:
        return int(user_id_str)
    except (ValueError, TypeError):
        return None


# -----------------------------------------------------------------------------
# JWT Error Handlers + Debug Logging
# -----------------------------------------------------------------------------
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"error": "Token has expired"}), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    auth_header = request.headers.get("Authorization", "NOT FOUND")
    print(f"[JWT] Invalid token error: {error}")
    print(f"[JWT] Authorization header received: {auth_header}")
    return (
        jsonify(
            {
                "error": f"Invalid token: {error}",
                "debug": {
                    "auth_header_present": auth_header != "NOT FOUND",
                    "auth_header_value": auth_header[:100]
                    if auth_header != "NOT FOUND"
                    else None,
                },
            }
        ),
        422,
    )


@jwt.unauthorized_loader
def missing_token_callback(error):
    print(f"[JWT] Missing token error: {error}")
    print(f"[JWT] Request headers: {dict(request.headers)}")
    return jsonify({"error": "Authorization token is missing"}), 401


@app.before_request
def log_request_info():
    """
    Debug middleware to log Authorization header for /api/* routes.
    Super useful while you are testing auth & recording.
    """
    if request.path.startswith("/api/"):
        auth_header = request.headers.get("Authorization", "NOT FOUND")
        print(f"Request: {request.method} {request.path}")
        if auth_header != "NOT FOUND":
            print(f"Authorization header: {auth_header[:80]}...")
        else:
            print("Authorization header: NOT FOUND")


# -----------------------------------------------------------------------------
# Health Check
# -----------------------------------------------------------------------------
@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "message": "API is running"}), 200


# Simple endpoint to test token manually if needed
@app.route("/api/debug/token", methods=["GET"])
@jwt_required()
def debug_token():
    from flask_jwt_extended import get_jwt

    try:
        user_id = get_jwt_identity()
        jwt_data = get_jwt()
        return jsonify({"user_id": user_id, "jwt_data": jwt_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -----------------------------------------------------------------------------
# Auth Routes
# -----------------------------------------------------------------------------
@app.route("/api/auth/register", methods=["POST"])
def register():
    """Register a new user"""
    try:
        data = request.get_json() or {}
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not username or not email or not password:
            return jsonify({"error": "Missing required fields"}), 400

        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already exists"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already exists"}), 400

        # Create user
        hashed_password = generate_password_hash(password)
        user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()

        # Identity must be a string for JWT
        access_token = create_access_token(identity=str(user.id))

        return (
            jsonify(
                {
                    "message": "User created successfully",
                    "access_token": access_token,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    },
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        print("[REGISTER ERROR]", e)
        return jsonify({"error": str(e)}), 500


@app.route("/api/auth/login", methods=["POST"])
def login():
    """Login user"""
    try:
        data = request.get_json() or {}
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Missing username or password"}), 400

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({"error": "Invalid credentials"}), 401

        access_token = create_access_token(identity=str(user.id))

        return (
            jsonify(
                {
                    "access_token": access_token,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        print("[LOGIN ERROR]", e)
        return jsonify({"error": str(e)}), 500


@app.route("/api/auth/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """Get current authenticated user"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"error": "Invalid token"}), 401

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        return (
            jsonify(
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "created_at": user.created_at.isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        import traceback

        print("[GET /api/auth/me ERROR]", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# -----------------------------------------------------------------------------
# Recording Routes
# -----------------------------------------------------------------------------
@app.route("/api/recordings/start", methods=["POST"])
@jwt_required()
def start_recording():
    """Start a new recording session (mic + Vosk + aggregator + summarizer)"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"error": "Invalid token"}), 401

        data = request.get_json() or {}
        title = data.get(
            "title", f"Recording {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        session_id = recording_service.start_session(user_id, title)

        return jsonify({"message": "Recording started", "session_id": session_id}), 200

    except Exception as e:
        import traceback

        print("[START RECORDING ERROR]", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/recordings/<session_id>/stop", methods=["POST"])
@jwt_required()
def stop_recording(session_id):
    """Stop recording and process transcription + summary + PDFs"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"error": "Invalid token"}), 401

        try:
            result = recording_service.stop_session(session_id, user_id)
        except Exception as e:
            import traceback

            print("[STOP SESSION ERROR]", e)
            traceback.print_exc()
            return jsonify({"error": f"Error stopping recording: {e}"}), 500

        if not result:
            return jsonify(
                {
                    "error": "Session not found, already stopped, or unauthorized",
                }
            ), 404

        transcript_pdf = None
        summary_pdf = None

        # Create transcript PDF if transcript file exists
        if result.get("transcript_file") and os.path.exists(result["transcript_file"]):
            try:
                transcript_pdf = pdf_generator.create_transcript_pdf(
                    result["transcript_file"], result["session_name"]
                )
            except Exception as e:
                print("[TRANSCRIPT PDF ERROR]", e)

        # Create summary PDF if summary file exists
        if result.get("summary_file") and os.path.exists(result["summary_file"]):
            try:
                summary_pdf = pdf_generator.create_summary_pdf(
                    result["summary_file"], result["session_name"]
                )
            except Exception as e:
                print("[SUMMARY PDF ERROR]", e)

        # Update DB with PDF paths
        recording = Recording.query.filter_by(session_id=session_id).first()
        if recording:
            if transcript_pdf:
                recording.transcript_pdf_path = transcript_pdf
            if summary_pdf:
                recording.summary_pdf_path = summary_pdf
            db.session.commit()

        return (
            jsonify(
                {
                    "message": "Recording stopped and processed",
                    "recording": {
                        "id": recording.id if recording else None,
                        "session_id": session_id,
                        "transcript_pdf": transcript_pdf,
                        "summary_pdf": summary_pdf,
                        "has_transcript": result.get("transcript_file") is not None,
                        "has_summary": result.get("summary_file") is not None,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        import traceback

        print("[STOP RECORDING ROUTE ERROR]", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/recordings/<session_id>/transcript", methods=["GET"])
@jwt_required()
def get_transcript(session_id):
    """
    Get real-time transcript for an active session.
    This reads from RecordingService.active_sessions aggregator.
    """
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"error": "Invalid token"}), 401

        transcript = recording_service.get_transcript(session_id, user_id)
        if transcript is None:
            return jsonify({"error": "Session not found or unauthorized"}), 404

        return jsonify({"transcript": transcript, "session_id": session_id}), 200

    except Exception as e:
        print("[GET TRANSCRIPT ERROR]", e)
        return jsonify({"error": str(e)}), 500


@app.route("/api/recordings", methods=["GET"])
@jwt_required()
def get_recordings():
    """List all recordings for the current user"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"error": "Invalid token"}), 401

        recordings = (
            Recording.query.filter_by(user_id=user_id)
            .order_by(Recording.created_at.desc())
            .all()
        )

        recordings_list = []
        for rec in recordings:
            recordings_list.append(
                {
                    "id": rec.id,
                    "session_id": rec.session_id,
                    "title": rec.title,
                    "created_at": rec.created_at.isoformat(),
                    "duration": rec.duration,
                    "status": rec.status,
                    "transcript_pdf_path": rec.transcript_pdf_path,
                    "summary_pdf_path": rec.summary_pdf_path,
                    "audio_file_path": rec.audio_file_path,
                }
            )

        return jsonify({"recordings": recordings_list}), 200

    except Exception as e:
        import traceback

        print("[GET RECORDINGS ERROR]", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/recordings/<recording_id>", methods=["GET"])
@jwt_required()
def get_recording(recording_id):
    """Get details (including transcript & summary text) for one recording"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"error": "Invalid token"}), 401

        recording = Recording.query.filter_by(id=recording_id, user_id=user_id).first()
        if not recording:
            return jsonify({"error": "Recording not found"}), 404

        transcript_text = None
        summary_text = None

        if recording.transcript_file_path and os.path.exists(
            recording.transcript_file_path
        ):
            with open(recording.transcript_file_path, "r", encoding="utf-8") as f:
                transcript_text = f.read()

        if recording.summary_file_path and os.path.exists(recording.summary_file_path):
            with open(recording.summary_file_path, "r", encoding="utf-8") as f:
                summary_text = f.read()

        return (
            jsonify(
                {
                    "recording": {
                        "id": recording.id,
                        "session_id": recording.session_id,
                        "title": recording.title,
                        "created_at": recording.created_at.isoformat(),
                        "duration": recording.duration,
                        "status": recording.status,
                        "transcript": transcript_text,
                        "summary": summary_text,
                        "transcript_pdf_path": recording.transcript_pdf_path,
                        "summary_pdf_path": recording.summary_pdf_path,
                        "audio_file_path": recording.audio_file_path,
                    }
                }
            ),
            200,
        )

    except Exception as e:
        print("[GET RECORDING ERROR]", e)
        return jsonify({"error": str(e)}), 500


@app.route("/api/recordings/<recording_id>/pdf/transcript", methods=["GET"])
@jwt_required()
def download_transcript_pdf(recording_id):
    """Download transcript PDF"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"error": "Invalid token"}), 401

        recording = Recording.query.filter_by(id=recording_id, user_id=user_id).first()
        if not recording:
            return jsonify({"error": "Recording not found"}), 404

        if not recording.transcript_pdf_path or not os.path.exists(
            recording.transcript_pdf_path
        ):
            return jsonify({"error": "PDF not found"}), 404

        return send_file(
            recording.transcript_pdf_path,
            as_attachment=True,
            download_name=f"transcript_{recording.session_id}.pdf",
            mimetype="application/pdf",
        )

    except Exception as e:
        print("[DOWNLOAD TRANSCRIPT PDF ERROR]", e)
        return jsonify({"error": str(e)}), 500


@app.route("/api/recordings/<recording_id>/pdf/summary", methods=["GET"])
@jwt_required()
def download_summary_pdf(recording_id):
    """Download summary PDF"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"error": "Invalid token"}), 401

        recording = Recording.query.filter_by(id=recording_id, user_id=user_id).first()
        if not recording:
            return jsonify({"error": "Recording not found"}), 404

        if not recording.summary_pdf_path or not os.path.exists(
            recording.summary_pdf_path
        ):
            return jsonify({"error": "PDF not found"}), 404

        return send_file(
            recording.summary_pdf_path,
            as_attachment=True,
            download_name=f"summary_{recording.session_id}.pdf",
            mimetype="application/pdf",
        )

    except Exception as e:
        print("[DOWNLOAD SUMMARY PDF ERROR]", e)
        return jsonify({"error": str(e)}), 500


@app.route("/api/recordings/<recording_id>/audio", methods=["GET"])
@jwt_required()
def get_audio_file(recording_id):
    """Stream audio file for playback"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"error": "Invalid token"}), 401

        recording = Recording.query.filter_by(id=recording_id, user_id=user_id).first()
        if not recording:
            return jsonify({"error": "Recording not found"}), 404

        if not recording.audio_file_path or not os.path.exists(
            recording.audio_file_path
        ):
            return jsonify({"error": "Audio file not found"}), 404

        return send_file(
            recording.audio_file_path,
            as_attachment=False,
            mimetype="audio/wav",
            conditional=True,
        )

    except Exception as e:
        import traceback

        print("[GET AUDIO FILE ERROR]", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/recordings/<recording_id>", methods=["DELETE"])
@jwt_required()
def delete_recording(recording_id):
    """Delete a recording and all associated files"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"error": "Invalid token"}), 401

        recording = Recording.query.filter_by(id=recording_id, user_id=user_id).first()
        if not recording:
            return jsonify({"error": "Recording not found"}), 404

        # Delete files from disk
        recording_service.delete_recording_files(recording)

        # Delete DB row
        db.session.delete(recording)
        db.session.commit()

        return jsonify({"message": "Recording deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        print("[DELETE RECORDING ERROR]", e)
        return jsonify({"error": str(e)}), 500


# -----------------------------------------------------------------------------
# File Upload Routes
# -----------------------------------------------------------------------------
@app.route("/api/upload/audio", methods=["POST"])
@jwt_required()
def upload_audio():
    """Upload audio file for transcription"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"error": "Invalid token"}), 401
        
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        title = request.form.get('title', '')
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not file_upload_service.allowed_file(file.filename, 'audio'):
            return jsonify({"error": "Invalid file type. Allowed: WAV, MP3, OGG, FLAC, M4A"}), 400
        
        # Save file
        file_path, original_filename = file_upload_service.save_uploaded_file(file, user_id)
        
        # Process file
        result = file_upload_service.process_uploaded_file(
            file_path, 'audio', original_filename, user_id, title
        )
        
        # Generate PDFs
        recording = Recording.query.get(result['recording_id'])
        if recording:
            try:
                transcript_pdf = pdf_generator.create_transcript_pdf(
                    result['transcript_file'], result['session_id']
                )
                recording.transcript_pdf_path = transcript_pdf
            except Exception as e:
                print(f"[TRANSCRIPT PDF ERROR] {e}")
            
            try:
                summary_pdf = pdf_generator.create_summary_pdf(
                    result['summary_file'], result['session_id']
                )
                recording.summary_pdf_path = summary_pdf
            except Exception as e:
                print(f"[SUMMARY PDF ERROR] {e}")
            
            db.session.commit()
        
        return jsonify({
            "message": "Audio file uploaded and processed successfully",
            "recording_id": result['recording_id'],
            "session_id": result['session_id']
        }), 201
        
    except Exception as e:
        import traceback
        print("[UPLOAD AUDIO ERROR]", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/upload/text", methods=["POST"])
@jwt_required()
def upload_text():
    """Upload PDF or TXT file for summarization"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"error": "Invalid token"}), 401
        
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        title = request.form.get('title', '')
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not file_upload_service.allowed_file(file.filename, 'text'):
            return jsonify({"error": "Invalid file type. Allowed: PDF, TXT"}), 400
        
        # Determine file type
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        file_type = 'pdf' if file_ext == 'pdf' else 'txt'
        
        # Save file
        file_path, original_filename = file_upload_service.save_uploaded_file(file, user_id)
        
        # Process file
        result = file_upload_service.process_uploaded_file(
            file_path, file_type, original_filename, user_id, title
        )
        
        # Generate PDFs
        recording = Recording.query.get(result['recording_id'])
        if recording:
            try:
                transcript_pdf = pdf_generator.create_transcript_pdf(
                    result['transcript_file'], result['session_id']
                )
                recording.transcript_pdf_path = transcript_pdf
            except Exception as e:
                print(f"[TRANSCRIPT PDF ERROR] {e}")
            
            try:
                summary_pdf = pdf_generator.create_summary_pdf(
                    result['summary_file'], result['session_id']
                )
                recording.summary_pdf_path = summary_pdf
            except Exception as e:
                print(f"[SUMMARY PDF ERROR] {e}")
            
            db.session.commit()
        
        return jsonify({
            "message": "Text file uploaded and processed successfully",
            "recording_id": result['recording_id'],
            "session_id": result['session_id']
        }), 201
        
    except Exception as e:
        import traceback
        print("[UPLOAD TEXT ERROR]", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Host 0.0.0.0 for cross-device testing on LAN
    app.run(debug=True, host="0.0.0.0", port=5000)
