# Deployment Checklist for summarizer.sbs

Quick reference checklist for deploying to Hostinger. See `HOSTINGER_DEPLOYMENT.md` for detailed instructions.

---

## Pre-Deployment

- [ ] **Purchase Hostinger VPS**
  - VPS 1 (2GB RAM) minimum
  - VPS 2 (4GB RAM) recommended
  - Choose Ubuntu 22.04 LTS

- [ ] **Save VPS Credentials**
  - IP Address: `___________________`
  - Root Password: `___________________`
  - SSH Port: `22` (default)

---

## DNS Configuration (Hostinger Panel)

- [ ] **Add A Records** (use your VPS IP)
  ```
  Type: A    | Name: @   | Value: YOUR_VPS_IP
  Type: A    | Name: www | Value: YOUR_VPS_IP
  Type: CNAME | Name: api | Value: summarizer.sbs
  ```

- [ ] **Wait for DNS Propagation** (15-30 minutes)
  - Check: https://dnschecker.org

---

## VPS Setup (SSH into VPS)

- [ ] **Connect via SSH**
  ```bash
  ssh root@YOUR_VPS_IP
  ```

- [ ] **Update system**
  ```bash
  apt update && apt upgrade -y
  ```

- [ ] **Install Docker**
  ```bash
  curl -fsSL https://get.docker.com -o get-docker.sh
  sh get-docker.sh
  apt install docker-compose -y
  ```

- [ ] **Install additional tools**
  ```bash
  apt install -y git nginx certbot python3-certbot-nginx ufw
  ```

- [ ] **Configure firewall**
  ```bash
  ufw allow 22/tcp
  ufw allow 80/tcp
  ufw allow 443/tcp
  ufw --force enable
  ```

---

## Application Deployment

- [ ] **Upload application to VPS**

  **Option A: Git Clone (recommended)**
  ```bash
  cd /var/www
  git clone YOUR_REPO_URL meeting-notes-summarizer
  ```

  **Option B: SCP from local machine**
  ```bash
  # From local Windows machine
  scp -r "D:\GenAI\Meeting notes summarizer" root@YOUR_VPS_IP:/var/www/meeting-notes-summarizer
  ```

- [ ] **Configure environment variables**
  ```bash
  cd /var/www/meeting-notes-summarizer
  nano .env
  ```

  **Update these critical values:**
  - [ ] `DEBUG=False`
  - [ ] `ENVIRONMENT=production`
  - [ ] `POSTGRES_PASSWORD=` (generate strong password)
  - [ ] `DATABASE_URL=` (update with new password)
  - [ ] `SECRET_KEY=` (generate: `python3 -c "import secrets; print(secrets.token_urlsafe(64))"`)
  - [ ] `CORS_ORIGINS=https://summarizer.sbs,https://www.summarizer.sbs,https://api.summarizer.sbs`
  - [ ] `OPENAI_API_KEY=` (your key)
  - [ ] `REDIS_HOST=redis` (not localhost in Docker)
  - [ ] `POSTGRES_HOST=postgres` (not localhost in Docker)

- [ ] **Configure frontend API URL**
  ```bash
  nano frontend/.env
  ```
  Add: `VITE_API_URL=https://api.summarizer.sbs`

- [ ] **Build and start services**
  ```bash
  cd frontend
  npm install
  npm run build
  cd ..

  docker-compose up -d --build
  docker-compose ps  # Verify all services are running
  ```

---

## Nginx Configuration

- [ ] **Create Nginx config**
  ```bash
  nano /etc/nginx/sites-available/summarizer.sbs
  ```
  Copy configuration from `HOSTINGER_DEPLOYMENT.md` Part 4

- [ ] **Enable site**
  ```bash
  ln -s /etc/nginx/sites-available/summarizer.sbs /etc/nginx/sites-enabled/
  nginx -t
  systemctl restart nginx
  ```

---

## SSL Certificate (Let's Encrypt)

- [ ] **Obtain SSL certificate**
  ```bash
  certbot --nginx -d summarizer.sbs -d www.summarizer.sbs -d api.summarizer.sbs
  ```
  - Enter email address
  - Agree to terms
  - Choose option 2: Redirect HTTP to HTTPS

- [ ] **Test auto-renewal**
  ```bash
  certbot renew --dry-run
  ```

---

## Testing

- [ ] **Test backend API**
  ```bash
  curl https://api.summarizer.sbs/api/v1/health
  ```
  Expected: `{"status": "healthy", ...}`

- [ ] **Test frontend**
  - Open: https://summarizer.sbs
  - Should see React app

- [ ] **Test recording feature**
  - Click "Listen" button
  - Record audio
  - Verify transcription works

- [ ] **Test file upload**
  - Upload audio file
  - Verify summarization works

- [ ] **Check API docs**
  - https://api.summarizer.sbs/api/docs (Swagger)
  - https://api.summarizer.sbs/api/redoc (ReDoc)

---

## Post-Deployment

- [ ] **Set up database backups**
  ```bash
  # Manual backup
  docker-compose exec postgres pg_dump -U meetingnotes_prod meeting_notes_db > backup_$(date +%Y%m%d).sql
  ```

- [ ] **Monitor application**
  ```bash
  docker-compose logs -f
  ```

- [ ] **Check disk space**
  ```bash
  df -h
  ```

- [ ] **Optional: Set up monitoring**
  - UptimeRobot for uptime monitoring
  - Sentry for error tracking

---

## Security Verification

- [ ] `DEBUG=False` in production .env
- [ ] Strong `SECRET_KEY` generated
- [ ] Strong database password set
- [ ] UFW firewall enabled
- [ ] SSL/HTTPS working on all domains
- [ ] `.env` not committed to Git (check `.gitignore`)
- [ ] Only ports 22, 80, 443 open

---

## Troubleshooting Quick Reference

**502 Bad Gateway?**
```bash
docker-compose ps
docker-compose restart
```

**DNS not working?**
- Wait 24-48 hours
- Check https://dnschecker.org

**SSL error?**
```bash
certbot renew
systemctl restart nginx
```

**Check logs:**
```bash
docker-compose logs backend
docker-compose logs postgres
nginx -t
journalctl -u nginx
```

---

## Important URLs

- **Frontend:** https://summarizer.sbs
- **API:** https://api.summarizer.sbs
- **API Docs:** https://api.summarizer.sbs/api/docs
- **Health Check:** https://api.summarizer.sbs/api/v1/health
- **Hostinger Panel:** https://hpanel.hostinger.com
- **DNS Checker:** https://dnschecker.org

---

## Estimated Timeline

- VPS setup: 30 minutes
- DNS propagation: 15-30 minutes (up to 24 hours)
- Application deployment: 20 minutes
- Nginx + SSL setup: 15 minutes
- Testing: 15 minutes
- **Total: ~2-3 hours** (excluding DNS propagation wait)

---

## Next Steps After Deployment

1. Test all features thoroughly
2. Set up automated backups (cron job)
3. Configure monitoring alerts
4. Add custom branding to frontend
5. Share your app: https://summarizer.sbs

---

**Full Guide:** See `HOSTINGER_DEPLOYMENT.md` for detailed step-by-step instructions.
