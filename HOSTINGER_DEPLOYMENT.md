# Hostinger Deployment Guide
## Deploying Meeting Notes Summarizer to summarizer.sbs

This guide covers deploying your application to Hostinger VPS and configuring the domain `summarizer.sbs`.

---

## Prerequisites

### 1. Hostinger Services Required
- ✅ Domain: `summarizer.sbs` (already purchased)
- 🔲 **Hostinger VPS** (required - shared hosting won't work)
  - Minimum: VPS 1 (2 GB RAM, 1 CPU)
  - Recommended: VPS 2 (4 GB RAM, 2 CPU) for better performance

### 2. Local Setup
- Docker and Docker Compose installed
- Git installed
- SSH client

---

## Part 1: Set Up Hostinger VPS

### Step 1: Purchase VPS Hosting
1. Log into Hostinger account
2. Go to **VPS** section
3. Choose a plan (VPS 1 or VPS 2 recommended)
4. Select **Ubuntu 22.04 LTS** as operating system
5. Complete purchase

### Step 2: Access VPS via SSH
After VPS is provisioned, Hostinger will provide:
- **IP Address** (e.g., 123.456.789.10)
- **Root Password** (via email or panel)
- **SSH Port** (usually 22)

Connect to your VPS:
```bash
ssh root@YOUR_VPS_IP
```

### Step 3: Initial VPS Setup

#### Update system
```bash
apt update && apt upgrade -y
```

#### Install Docker
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Verify installation
docker --version
docker-compose --version
```

#### Install additional tools
```bash
apt install -y git nginx certbot python3-certbot-nginx ufw
```

#### Configure firewall
```bash
# Allow SSH, HTTP, HTTPS
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
```

---

## Part 2: Configure DNS Records

### Step 1: Access Hostinger DNS Management
1. Log into Hostinger panel
2. Go to **Domains** → select `summarizer.sbs`
3. Click **DNS / Nameservers** → **Manage DNS records**

### Step 2: Add DNS Records

**Replace `YOUR_VPS_IP` with your actual VPS IP address**

| Type | Name | Value | TTL |
|------|------|-------|-----|
| **A** | @ | `YOUR_VPS_IP` | 3600 |
| **A** | www | `YOUR_VPS_IP` | 3600 |
| **CNAME** | api | summarizer.sbs | 3600 |

**Example:**
- If VPS IP is `123.456.789.10`:
  - `summarizer.sbs` → `123.456.789.10`
  - `www.summarizer.sbs` → `123.456.789.10`
  - `api.summarizer.sbs` → `summarizer.sbs`

### Step 3: Wait for DNS Propagation
- Usually takes 15-30 minutes
- Can take up to 24-48 hours globally
- Check status: https://dnschecker.org (search for `summarizer.sbs`)

---

## Part 3: Deploy Application to VPS

### Step 1: Clone Repository on VPS
```bash
# Create application directory
mkdir -p /var/www
cd /var/www

# Clone your repository (replace with your Git URL)
git clone https://github.com/yourusername/meeting-notes-summarizer.git
cd meeting-notes-summarizer
```

**Alternative: Upload via SCP from local machine**
```bash
# From your local machine
scp -r "D:\GenAI\Meeting notes summarizer" root@YOUR_VPS_IP:/var/www/meeting-notes-summarizer
```

### Step 2: Configure Environment Variables
```bash
cd /var/www/meeting-notes-summarizer

# Create production .env file
nano .env
```

**Update the following values in `.env`:**
```bash
# Application Settings
APP_NAME="Meeting Notes Summarizer"
APP_VERSION="0.1.0"
DEBUG=False  # ⚠️ IMPORTANT: Set to False in production
ENVIRONMENT=production

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Database Configuration
POSTGRES_USER=meetingnotes_prod
POSTGRES_PASSWORD=GENERATE_STRONG_PASSWORD_HERE  # Change this!
POSTGRES_DB=meeting_notes_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
DATABASE_URL=postgresql://meetingnotes_prod:YOUR_PASSWORD@postgres:5432/meeting_notes_db

# AI Service API Keys
OPENAI_API_KEY=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

# AI Model Configuration
CLAUDE_MODEL=claude-3-5-sonnet-20241022
GPT_MODEL=gpt-4o-mini
WHISPER_MODEL=whisper-1

# File Upload Settings
MAX_UPLOAD_SIZE_MB=100
ALLOWED_AUDIO_FORMATS=mp3,wav,m4a,mp4,webm
UPLOAD_DIR=./uploads

# Processing Settings
MAX_AUDIO_DURATION_MINUTES=120
PROCESSING_TIMEOUT_SECONDS=600

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_URL=redis://redis:6379/0

# CORS Settings (⚠️ UPDATE WITH YOUR DOMAIN)
CORS_ORIGINS=https://summarizer.sbs,https://www.summarizer.sbs,https://api.summarizer.sbs
CORS_ALLOW_CREDENTIALS=True
CORS_ALLOW_METHODS=*
CORS_ALLOW_HEADERS=*

# Security (⚠️ GENERATE NEW SECRET KEY)
SECRET_KEY=GENERATE_LONG_RANDOM_STRING_HERE  # Change this!
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Generate a strong secret key:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

Save and exit (`Ctrl+X`, then `Y`, then `Enter`)

### Step 3: Update Frontend API URL
```bash
nano frontend/.env
```

Add:
```bash
VITE_API_URL=https://api.summarizer.sbs
```

### Step 4: Build and Start Services
```bash
# Build frontend
cd frontend
npm install
npm run build
cd ..

# Start all services with Docker Compose
docker-compose up -d --build

# Check if services are running
docker-compose ps

# View logs
docker-compose logs -f
```

---

## Part 4: Configure Nginx Reverse Proxy

### Step 1: Create Nginx Configuration
```bash
nano /etc/nginx/sites-available/summarizer.sbs
```

**Add this configuration:**
```nginx
# Frontend - Main domain
server {
    listen 80;
    listen [::]:80;
    server_name summarizer.sbs www.summarizer.sbs;

    # Serve frontend static files
    root /var/www/meeting-notes-summarizer/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # File upload size limit (match MAX_UPLOAD_SIZE_MB)
    client_max_body_size 100M;
}

# Backend API - api subdomain
server {
    listen 80;
    listen [::]:80;
    server_name api.summarizer.sbs;

    # Proxy to FastAPI backend
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # File upload size limit
    client_max_body_size 100M;
}
```

### Step 2: Enable Site
```bash
# Create symbolic link
ln -s /etc/nginx/sites-available/summarizer.sbs /etc/nginx/sites-enabled/

# Test configuration
nginx -t

# Restart Nginx
systemctl restart nginx
```

---

## Part 5: Set Up SSL/HTTPS with Let's Encrypt

### Step 1: Obtain SSL Certificate
```bash
# Get certificates for all domains
certbot --nginx -d summarizer.sbs -d www.summarizer.sbs -d api.summarizer.sbs

# Follow prompts:
# - Enter email address
# - Agree to terms
# - Choose: Redirect HTTP to HTTPS (option 2)
```

### Step 2: Verify SSL
Visit:
- https://summarizer.sbs ✅
- https://www.summarizer.sbs ✅
- https://api.summarizer.sbs/api/v1/health ✅

### Step 3: Auto-Renewal (Already configured by certbot)
```bash
# Test renewal
certbot renew --dry-run

# Renewal happens automatically via cron
```

---

## Part 6: Testing Deployment

### Backend API Test
```bash
curl https://api.summarizer.sbs/api/v1/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "database": "healthy"
}
```

### Frontend Test
1. Open browser: https://summarizer.sbs
2. Should see React application
3. Click "Listen" button to test recording
4. Upload audio file to test full pipeline

### API Documentation
- Swagger: https://api.summarizer.sbs/api/docs
- ReDoc: https://api.summarizer.sbs/api/redoc

---

## Part 7: Maintenance & Monitoring

### View Application Logs
```bash
cd /var/www/meeting-notes-summarizer
docker-compose logs -f backend
docker-compose logs -f postgres
```

### Restart Services
```bash
docker-compose restart
```

### Update Application
```bash
cd /var/www/meeting-notes-summarizer
git pull origin main
docker-compose down
docker-compose up -d --build
```

### Database Backup
```bash
# Create backup
docker-compose exec postgres pg_dump -U meetingnotes_prod meeting_notes_db > backup_$(date +%Y%m%d).sql

# Restore backup
docker-compose exec -T postgres psql -U meetingnotes_prod meeting_notes_db < backup_20241228.sql
```

### Monitor Disk Space
```bash
df -h
docker system prune -a  # Clean up old images
```

---

## Troubleshooting

### Issue: DNS not resolving
**Solution:**
- Wait 24-48 hours for full propagation
- Check DNS records in Hostinger panel
- Verify nameservers point to Hostinger

### Issue: 502 Bad Gateway
**Solution:**
```bash
# Check if backend is running
docker-compose ps
curl http://localhost:8000/api/v1/health

# Restart services
docker-compose restart
```

### Issue: SSL certificate error
**Solution:**
```bash
# Renew certificate
certbot renew
systemctl restart nginx
```

### Issue: File upload fails
**Solution:**
- Check `client_max_body_size` in Nginx config
- Verify `MAX_UPLOAD_SIZE_MB` in `.env`
- Check disk space: `df -h`

### Issue: Database connection error
**Solution:**
```bash
# Check PostgreSQL container
docker-compose logs postgres
docker-compose restart postgres
```

---

## Security Checklist

- ✅ Changed `SECRET_KEY` in `.env`
- ✅ Changed database password
- ✅ Set `DEBUG=False` in production
- ✅ Enabled UFW firewall
- ✅ SSL/HTTPS enabled
- ✅ Regular backups configured
- ⚠️ **IMPORTANT:** Never commit `.env` with production secrets to Git

---

## Cost Estimation

**Monthly costs:**
- Hostinger VPS 1: ~$4.99/month
- Hostinger VPS 2: ~$8.99/month
- Domain: ~$0.99/year (promotional, then ~$9.99/year)
- OpenAI API: Variable (depends on usage)
  - Whisper: $0.006 per minute of audio
  - GPT-4o-mini: ~$0.15 per 1M tokens
- Anthropic API: Variable
  - Claude Sonnet: ~$3 per 1M input tokens

**Example usage:**
- 100 meetings/month × 30 min each = $18/month (Whisper)
- Summarization: ~$5-10/month (GPT/Claude)
- **Total: ~$30-40/month**

---

## Next Steps

1. ✅ Purchase Hostinger VPS
2. ✅ Configure DNS records
3. ✅ Deploy application
4. ✅ Set up SSL
5. 🔲 Test all features
6. 🔲 Set up monitoring (optional: UptimeRobot, Sentry)
7. 🔲 Configure automated backups
8. 🔲 Add custom branding to frontend

---

## Support

**Issues?**
- Hostinger Support: https://www.hostinger.com/help
- Application Issues: Check logs with `docker-compose logs`

**Need Help?**
Create an issue in your repository with:
- Error messages
- Steps to reproduce
- Relevant logs
