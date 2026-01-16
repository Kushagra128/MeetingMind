"""
Quick test script to verify JWT token creation and validation
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import app, jwt
from flask_jwt_extended import create_access_token, decode_token
from database import db, User

with app.app_context():
    # Create a test user if doesn't exist
    test_user = User.query.filter_by(username='test').first()
    if not test_user:
        from werkzeug.security import generate_password_hash
        test_user = User(
            username='test',
            email='test@test.com',
            password_hash=generate_password_hash('test123')
        )
        db.session.add(test_user)
        db.session.commit()
    
    # Create a token
    token = create_access_token(identity=test_user.id)
    print(f"Created token: {token[:50]}...")
    
    # Try to decode it
    try:
        decoded = decode_token(token)
        print(f"Token decoded successfully!")
        print(f"User ID: {decoded.get('sub')}")
        print(f"Token is valid!")
    except Exception as e:
        print(f"Error decoding token: {e}")



