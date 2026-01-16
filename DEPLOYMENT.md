# MeetingMing Deployment Guide

This guide covers multiple deployment options for MeetingMing, from simple local deployment to production cloud hosting.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Production Build](#local-production-build)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment Options](#cloud-deployment-options)
5. [Environment Configuration](#environment-configuration)
6. [Security Checklist](#security-checklist)

---

## Prerequisites

Before deploying, ensure you have:

- Python 3.7+ installed
- Node.js 16+ and npm installed
- Git installed
- Domain name (for production deployment)
- SSL certificate (for HTTPS in production)

---

## 1. Local Production Build

### Step 1: Build Frontend

```bash
cd frontend
npm install
npm run build
```

This creates a `frontend/dist` folder with optimized static files.

### Step 2: Serve Frontend with Backend

Option A: Use Flask to serve static files (simple, single server)

Edit `backend/app.py` to add static file serving:

```python
from flask import send_from_directory

# Add after app initialization
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path and os.path.exists(os.path.join('../frontend/dist', path)):
        return send_from_directory('../frontend/dist', path)
    return send_from_directory('../frontend/dist', 'index.html')
```

Then run:

```bash
cd backend
python app.py
```

Access at: `http://localhost:5000`

Option B: Use separate web server (recommended for production)

Use Nginx or Apache to serve frontend and proxy API requests to Flask.

---

## 2. Docker Deployment

### Create Dockerfile for Backend

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for PyAudio
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    python3-pyaudio \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy iot-meeting-minutes module
COPY ../iot-meeting-minutes /app/iot-meeting-minutes

# Copy models
COPY ../models /app/models

# Create necessary directories
RUN mkdir -p /app/uploads /app/data

EXPOSE 5000

CMD ["python", "app.py"]
```

### Create Dockerfile for Frontend

Create `frontend/Dockerfile`:

```dockerfile
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Production stage with Nginx
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Create Nginx Config

Create `frontend/nginx.conf`:

```nginx
server {
    listen 80;
    server_name localhost;

    root /usr/share/nginx/html;
    index index.html;

    # Frontend routes
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to backend
    location /api {
        proxy_pass http://backend:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Create Docker Compose

Create `docker-compose.yml` in root:

```yaml
version: "3.8"

services:
  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    container_name: meetingming-backend
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./backend/uploads:/app/uploads
      - ./iot-meeting-minutes/recordings:/app/iot-meeting-minutes/recordings
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - FLASK_ENV=production
    restart: unless-stopped

  frontend:
    build:
      context: frontend
      dockerfile: Dockerfile
    container_name: meetingming-frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  data:
  uploads:
  recordings:
```

### Deploy with Docker

```bash
# Create .env file with secrets
echo "SECRET_KEY=$(openssl rand -hex 32)" > .env
echo "JWT_SECRET_KEY=$(openssl rand -hex 32)" >> .env

# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

Access at: `http://localhost`

---

## 3. Cloud Deployment Options

### Option A: AWS EC2

1. **Launch EC2 Instance**
   - Choose Ubuntu 22.04 LTS
   - Instance type: t3.medium or larger (for Vosk model)
   - Configure security groups: Allow ports 80, 443, 22

2. **Connect and Setup**

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone your repository
git clone https://github.com/yourusername/meetingming.git
cd meetingming

# Deploy
docker-compose up -d
```

3. **Setup Domain and SSL**

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com
```

### Option B: DigitalOcean Droplet

Similar to AWS EC2, but with simpler interface:

1. Create Droplet (Ubuntu 22.04, 4GB RAM minimum)
2. Follow same Docker setup as EC2
3. Point your domain to Droplet IP
4. Setup SSL with Certbot

### Option C: Heroku

1. **Prepare for Heroku**

Create `Procfile` in root:

```
web: cd backend && gunicorn app:app
```

Add to `backend/requirements.txt`:

```
gunicorn>=20.1.0
```

2. **Deploy**

```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
heroku create meetingming-app

# Set environment variables
heroku config:set SECRET_KEY=$(openssl rand -hex 32)
heroku config:set JWT_SECRET_KEY=$(openssl rand -hex 32)

# Deploy
git push heroku main

# Open app
heroku open
```

**Note**: Heroku's ephemeral filesystem means uploaded files will be lost on restart. Use S3 for file storage in production.

### Option D: Railway.app

1. Go to [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Railway auto-detects and deploys
4. Add environment variables in dashboard
5. Get automatic HTTPS domain

### Option E: Render.com

1. Go to [render.com](https://render.com)
2. Create new Web Service
3. Connect repository
4. Configure:
   - Build Command: `cd frontend && npm install && npm run build && cd ../backend && pip install -r requirements.txt`
   - Start Command: `cd backend && python app.py`
5. Add environment variables
6. Deploy

---

## 4. Environment Configuration

### Production Environment Variables

Create `.env` file:

```env
# Security
SECRET_KEY=your-super-secret-key-change-this
JWT_SECRET_KEY=your-jwt-secret-key-change-this

# Flask
FLASK_ENV=production
FLASK_DEBUG=0

# Database (if using PostgreSQL)
DATABASE_URL=postgresql://user:password@localhost/meetingming

# File Storage (if using S3)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_BUCKET=meetingming-uploads
AWS_REGION=us-east-1

# CORS (update with your domain)
CORS_ORIGINS=https://yourdomain.com

# Optional: Email for notifications
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Update Backend for Production

Edit `backend/app.py`:

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Use environment variables
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")

# Update CORS for production
CORS(
    app,
    origins=os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(","),
    supports_credentials=True,
)
```

### Update Frontend API URL

Create `frontend/.env.production`:

```env
VITE_API_URL=https://api.yourdomain.com
```

Update `frontend/src/main.jsx` or create API config:

```javascript
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";
```

---

## 5. Security Checklist

### Before Going Live

- [ ] Change all default secret keys
- [ ] Enable HTTPS/SSL
- [ ] Set secure CORS origins
- [ ] Use environment variables for secrets
- [ ] Enable rate limiting on API endpoints
- [ ] Set up database backups
- [ ] Configure firewall rules
- [ ] Use strong passwords for database
- [ ] Enable logging and monitoring
- [ ] Set up error tracking (Sentry, etc.)
- [ ] Implement file upload size limits
- [ ] Sanitize user inputs
- [ ] Use PostgreSQL instead of SQLite for production
- [ ] Set up regular security updates
- [ ] Configure CSP headers
- [ ] Enable CSRF protection

### Recommended Security Additions

Install Flask security extensions:

```bash
pip install flask-limiter flask-talisman python-dotenv
```

Add to `backend/app.py`:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Security headers (only in production)
if os.environ.get('FLASK_ENV') == 'production':
    Talisman(app, force_https=True)

# Apply rate limits to auth endpoints
@app.route("/api/auth/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    # ... existing code
```

---

## 6. Monitoring and Maintenance

### Setup Logging

```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/meetingming.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('MeetingMing startup')
```

### Database Backups

```bash
# SQLite backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
sqlite3 data/meeting_transcriber.db ".backup 'backups/db_backup_$DATE.db'"

# Keep only last 7 days
find backups/ -name "db_backup_*.db" -mtime +7 -delete
```

### Health Monitoring

Use tools like:

- **Uptime Robot** - Free uptime monitoring
- **New Relic** - Application performance monitoring
- **Sentry** - Error tracking
- **Prometheus + Grafana** - Metrics and dashboards

---

## Quick Start Commands

### Local Production

```bash
cd frontend && npm run build
cd ../backend && python app.py
```

### Docker

```bash
docker-compose up -d
```

### Check Status

```bash
# Docker
docker-compose ps
docker-compose logs -f

# System
systemctl status nginx
systemctl status meetingming
```

---

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 5000
lsof -i :5000
# Kill process
kill -9 <PID>
```

### Permission Denied

```bash
sudo chown -R $USER:$USER .
chmod +x setup.sh
```

### Database Locked

```bash
# Stop all processes using database
fuser -k data/meeting_transcriber.db
```

---

## Support

For deployment issues:

1. Check logs: `docker-compose logs` or `tail -f logs/meetingming.log`
2. Verify environment variables are set
3. Ensure all ports are open in firewall
4. Check disk space: `df -h`
5. Verify Python/Node versions

---

**Need help?** Check the main [README.md](README.md) and [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
