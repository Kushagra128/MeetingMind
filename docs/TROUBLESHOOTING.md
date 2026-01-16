# Troubleshooting Guide

## JWT Authentication Issues (422 Errors)

If you're getting 422 errors after login, follow these steps:

### 1. Clear Browser Storage
- Open browser DevTools (F12)
- Go to Application/Storage tab
- Clear Local Storage
- Clear Session Storage
- Refresh the page

### 2. Check Backend Logs
Look for error messages in the Flask console. Common issues:
- "Invalid token" - Token format issue
- "Token has expired" - Token expired
- "Authorization token is missing" - Token not sent

### 3. Verify Token is Being Sent
1. Open browser DevTools (F12)
2. Go to Network tab
3. Try to access a protected endpoint
4. Check the Request Headers - should see:
   ```
   Authorization: Bearer <token>
   ```

### 4. Test Token Manually
1. Login and copy the token from localStorage
2. Test with curl:
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:5000/api/auth/me
   ```

### 5. Check Flask-JWT-Extended Version
```bash
pip show flask-jwt-extended
```
Should be version 4.5.0 or higher.

### 6. Restart Both Servers
1. Stop backend (Ctrl+C)
2. Stop frontend (Ctrl+C)
3. Restart backend: `python app.py`
4. Restart frontend: `npm run dev`

### 7. Check CORS Configuration
Make sure in `backend/app.py`:
```python
CORS(app, 
     origins=["http://localhost:5173", "http://localhost:3000"],
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"])
```

### 8. Verify Database
The user should exist in the database:
```python
# In Python shell
from backend.database import db, User
from backend.app import app
with app.app_context():
    users = User.query.all()
    print(users)
```

## Common Solutions

### Solution 1: Re-register
1. Clear database: Delete `meeting_transcriber.db`
2. Restart backend
3. Register a new account
4. Try logging in

### Solution 2: Check Token Format
The token should be a long string. If it's null or empty, there's an issue with login.

### Solution 3: Verify Secret Keys
Make sure `JWT_SECRET_KEY` in backend matches (or use environment variables).

## Still Having Issues?

1. Check browser console for errors
2. Check Flask console for errors
3. Verify both servers are running
4. Try in incognito/private browsing mode
5. Check firewall/antivirus isn't blocking requests



