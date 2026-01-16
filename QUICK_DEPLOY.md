# Quick Deploy Guide

Get MeetingMing running in production in under 10 minutes.

## Option 1: Docker (Recommended - Easiest)

### Prerequisites

- Docker Desktop installed ([Download](https://www.docker.com/products/docker-desktop))
- 10GB free disk space

### Steps

1. **Clone or download the project**

   ```bash
   git clone https://github.com/yourusername/meetingming.git
   cd meetingming
   ```

2. **Run deployment script**

   **Windows:**

   ```cmd
   deploy.bat
   ```

   **Linux/Mac:**

   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

3. **Choose option 1** (Build and start containers)

4. **Wait 5-10 minutes** for the build to complete

5. **Access the app**
   - Frontend: http://localhost
   - Backend API: http://localhost:5000

That's it! 🎉

---

## Option 2: Manual Setup (Without Docker)

### Prerequisites

- Python 3.7+
- Node.js 16+
- 5GB free disk space

### Steps

1. **Setup Backend**

   ```bash
   cd backend
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate

   pip install -r requirements.txt
   ```

2. **Setup Frontend**

   ```bash
   cd frontend
   npm install
   npm run build
   ```

3. **Configure Environment**

   ```bash
   # Copy example env file
   copy .env.example .env  # Windows
   cp .env.example .env    # Linux/Mac

   # Edit .env and update SECRET_KEY and JWT_SECRET_KEY
   ```

4. **Run Backend**

   ```bash
   cd backend
   python app.py
   ```

5. **Serve Frontend**

   Install a simple HTTP server:

   ```bash
   npm install -g serve
   cd frontend
   serve -s dist -l 3000
   ```

6. **Access the app**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

---

## Option 3: Cloud Deployment (Production)

### Using Railway.app (Easiest Cloud Option)

1. **Sign up** at [railway.app](https://railway.app)

2. **Click "New Project"** → "Deploy from GitHub repo"

3. **Connect your repository**

4. **Add environment variables** in Railway dashboard:
   - `SECRET_KEY`: Generate with `openssl rand -hex 32`
   - `JWT_SECRET_KEY`: Generate with `openssl rand -hex 32`
   - `FLASK_ENV`: `production`

5. **Deploy** - Railway auto-detects and deploys

6. **Get your URL** - Railway provides a free domain

### Using DigitalOcean (More Control)

1. **Create Droplet**
   - Ubuntu 22.04
   - 4GB RAM minimum
   - $24/month

2. **SSH into server**

   ```bash
   ssh root@your-server-ip
   ```

3. **Install Docker**

   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   ```

4. **Install Docker Compose**

   ```bash
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

5. **Clone and deploy**

   ```bash
   git clone https://github.com/yourusername/meetingming.git
   cd meetingming

   # Create .env file
   nano .env
   # Add your SECRET_KEY and JWT_SECRET_KEY

   # Deploy
   docker-compose up -d
   ```

6. **Setup domain and SSL**

   ```bash
   # Install Certbot
   sudo apt install certbot python3-certbot-nginx -y

   # Get SSL certificate
   sudo certbot --nginx -d yourdomain.com
   ```

7. **Access your app** at https://yourdomain.com

---

## Troubleshooting

### Docker Issues

**"Port already in use"**

```bash
# Stop existing containers
docker-compose down

# Or change ports in docker-compose.yml
```

**"Cannot connect to Docker daemon"**

- Make sure Docker Desktop is running
- Restart Docker Desktop

**"Build failed"**

```bash
# Clean rebuild
docker-compose down
docker system prune -a
docker-compose up -d --build
```

### Manual Setup Issues

**"Module not found"**

```bash
# Make sure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt
```

**"Port 5000 already in use"**

```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

**"CORS error"**

- Update `CORS_ORIGINS` in `.env`
- Make sure frontend URL is included

### Cloud Deployment Issues

**"502 Bad Gateway"**

- Check if backend is running: `docker-compose ps`
- Check logs: `docker-compose logs backend`
- Verify environment variables are set

**"SSL certificate error"**

- Make sure DNS is pointing to your server
- Wait for DNS propagation (up to 48 hours)
- Try again: `sudo certbot --nginx -d yourdomain.com`

---

## Next Steps

After deployment:

1. **Create your first account** - Register a new user
2. **Test recording** - Try the live recording feature
3. **Upload a file** - Test file upload functionality
4. **Download PDFs** - Verify PDF generation works
5. **Check logs** - Monitor for any errors

---

## Getting Help

- **Documentation**: See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guide
- **Checklist**: Use [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- **Troubleshooting**: Check [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- **Issues**: Open an issue on GitHub

---

## Security Reminder

Before going live:

- ✅ Change all default secret keys
- ✅ Enable HTTPS
- ✅ Set proper CORS origins
- ✅ Use strong passwords
- ✅ Enable firewall
- ✅ Set up backups

See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for complete security checklist.
