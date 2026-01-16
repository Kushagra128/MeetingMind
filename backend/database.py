"""
Database models and initialization
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

db = SQLAlchemy()


class User(db.Model):
    """User model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    recordings = db.relationship('Recording', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'


class Recording(db.Model):
    """Recording model"""
    __tablename__ = 'recordings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    duration = db.Column(db.Float, default=0.0)  # Duration in seconds
    status = db.Column(db.String(20), default='recording')  # recording, processing, completed, failed
    
    # File paths
    audio_file_path = db.Column(db.String(500))
    transcript_file_path = db.Column(db.String(500))
    summary_file_path = db.Column(db.String(500))
    transcript_pdf_path = db.Column(db.String(500))
    summary_pdf_path = db.Column(db.String(500))
    metadata_file_path = db.Column(db.String(500))
    
    def __repr__(self):
        return f'<Recording {self.session_id}>'


def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return db

