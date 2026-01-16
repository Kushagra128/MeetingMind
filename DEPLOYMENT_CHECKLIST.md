# MeetingMing Deployment Checklist

Use this checklist to ensure a smooth deployment.

## Pre-Deployment

### Local Testing

- [ ] Test all features locally (register, login, recording, upload, PDF generation)
- [ ] Run frontend build: `cd frontend && npm run build`
- [ ] Test backend with production settings
- [ ] Verify database migrations work
- [ ] Test file uploads and downloads
- [ ] Check audio recording functionality

### Code Preparation

- [ ] Update version numbers
- [ ] Remove debug code and console.logs
- [ ] Update README.md with deployment info
- [ ] Commit all changes to Git
- [ ] Tag release version: `git tag v1.0.0`

## Environment Setup

### Configuration Files

- [ ] Copy `.env.example` to `.env`
- [ ] Generate secure SECRET_KEY: `openssl rand -hex 32`
- [ ] Generate secure JWT_SECRET_KEY: `openssl rand -hex 32`
- [ ] Update CORS_ORIGINS with production domain
- [ ] Set FLASK_ENV=production
- [ ] Set FLASK_DEBUG=0

### Frontend Configuration

- [ ] Update `frontend/.env.production` with production API URL
- [ ] Update any hardcoded URLs in code
- [ ] Configure proper error handling for production

## Docker Deployment

### Prerequisites

- [ ] Docker installed and running
- [ ] Docker Compose installed
- [ ] Sufficient disk space (at least 10GB free)
- [ ] Ports 80 and 5000 available

### Deployment Steps

- [ ] Run `deploy.bat` (Windows) or `bash deploy.sh` (Linux/Mac)
- [ ] Choose option 1: "Build and start containers"
- [ ] Wait for build to complete (may take 5-10 minutes first time)
- [ ] Verify containers are running: `docker-compose ps`
- [ ] Check logs for errors: `docker-compose logs -f`

### Testing

- [ ] Access frontend at http://localhost
- [ ] Test user registration
- [ ] Test user login
- [ ] Test recording functionality
- [ ] Test file upload
- [ ] Test PDF generation and download
- [ ] Test audio playback
- [ ] Verify all API endpoints work

## Cloud Deployment (AWS/DigitalOcean/etc.)

### Server Setup

- [ ] Launch server instance (minimum 4GB RAM, 2 CPU cores)
- [ ] Configure security groups/firewall (ports 22, 80, 443)
- [ ] SSH into server
- [ ] Update system: `sudo apt update && sudo apt upgrade -y`
- [ ] Install Docker and Docker Compose

### Domain and SSL

- [ ] Point domain DNS to server IP
- [ ] Wait for DNS propagation (can take up to 48 hours)
- [ ] Install Certbot: `sudo apt install certbot python3-certbot-nginx`
- [ ] Obtain SSL certificate: `sudo certbot --nginx -d yourdomain.com`
- [ ] Configure auto-renewal: `sudo certbot renew --dry-run`

### Application Deployment

- [ ] Clone repository: `git clone https://github.com/yourusername/meetingming.git`
- [ ] Navigate to directory: `cd meetingming`
- [ ] Create and configure `.env` file
- [ ] Update `frontend/.env.production` with production domain
- [ ] Run deployment script
- [ ] Configure Nginx for production (if not using Docker Nginx)
- [ ] Set up systemd service for auto-restart

### Monitoring

- [ ] Set up log rotation
- [ ] Configure monitoring (Uptime Robot, New Relic, etc.)
- [ ] Set up error tracking (Sentry)
- [ ] Configure backup schedule
- [ ] Set up alerts for downtime

## Security Hardening

### Application Security

- [ ] All secret keys are unique and secure
- [ ] HTTPS is enabled and enforced
- [ ] CORS is properly configured
- [ ] Rate limiting is enabled
- [ ] File upload validation is working
- [ ] SQL injection protection (using SQLAlchemy ORM)
- [ ] XSS protection headers are set
- [ ] CSRF protection is enabled

### Server Security

- [ ] SSH key authentication only (disable password auth)
- [ ] Firewall is configured (UFW or security groups)
- [ ] Fail2ban is installed and configured
- [ ] Regular security updates are enabled
- [ ] Non-root user for running application
- [ ] Database backups are automated
- [ ] File backups are automated

## Post-Deployment

### Verification

- [ ] All features work on production
- [ ] SSL certificate is valid
- [ ] Performance is acceptable
- [ ] Error pages display correctly
- [ ] Mobile responsiveness works
- [ ] Cross-browser compatibility verified

### Documentation

- [ ] Update deployment documentation
- [ ] Document any custom configurations
- [ ] Create runbook for common issues
- [ ] Document backup and restore procedures
- [ ] Share access credentials securely with team

### Monitoring Setup

- [ ] Uptime monitoring is active
- [ ] Error tracking is receiving data
- [ ] Log aggregation is working
- [ ] Disk space alerts are configured
- [ ] Performance metrics are being collected

## Maintenance

### Regular Tasks

- [ ] Weekly: Check logs for errors
- [ ] Weekly: Verify backups are working
- [ ] Monthly: Update dependencies
- [ ] Monthly: Review security advisories
- [ ] Quarterly: Review and optimize performance
- [ ] Quarterly: Test disaster recovery procedures

### Backup Schedule

- [ ] Daily: Database backups
- [ ] Daily: User uploads backup
- [ ] Weekly: Full system backup
- [ ] Monthly: Offsite backup copy

## Rollback Plan

### If Deployment Fails

1. [ ] Stop containers: `docker-compose down`
2. [ ] Check logs: `docker-compose logs`
3. [ ] Fix issues in code
4. [ ] Rebuild: `docker-compose build --no-cache`
5. [ ] Restart: `docker-compose up -d`

### If Production Issues Occur

1. [ ] Revert to previous Git tag: `git checkout v1.0.0`
2. [ ] Rebuild and redeploy
3. [ ] Restore database from backup if needed
4. [ ] Investigate and fix issues in development
5. [ ] Test thoroughly before redeploying

## Support Contacts

- **Hosting Provider**: [Provider name and support URL]
- **Domain Registrar**: [Registrar name and support URL]
- **SSL Certificate**: [Certificate provider]
- **Monitoring Service**: [Service name and dashboard URL]

## Notes

Add any deployment-specific notes here:

---

**Last Updated**: [Date]
**Deployed By**: [Name]
**Version**: [Version number]
