# Quick Deploy to Hostinger VM

Step-by-step commands to pull your code to Hostinger VPS and deploy.

---

## Step 1: Connect to Hostinger VPS via SSH

### From Windows (PowerShell or Command Prompt)

```bash
ssh root@YOUR_VPS_IP
```

**Replace `YOUR_VPS_IP` with your actual VPS IP address from Hostinger panel.**

When prompted:
- Type `yes` to accept the fingerprint (first time only)
- Enter your root password (from Hostinger email/panel)

---

## Step 2: Initial VPS Setup (First Time Only)

### Install Required Software

```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install -y docker-compose

# Install Nginx, Certbot, and other tools
apt install -y git nginx certbot python3-certbot-nginx ufw nano

# Configure firewall
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Verify installations
docker --version
docker-compose --version
nginx -v
```

---

## Step 3: Clone Your Repository

### Option A: Clone Repository (First Time)

```bash
# Create directory
mkdir -p /var/www
cd /var/www

# Clone your repository
git clone https://github.com/3aiwarrior/Meeting-notes-summarizer.git meeting-notes-summarizer

# Navigate to project
cd meeting-notes-summarizer
```

### Option B: Pull Latest Changes (If Already Cloned)

```bash
# Navigate to project
cd /var/www/meeting-notes-summarizer

# Pull latest changes
git pull origin main

# If you need to reset local changes first
git fetch origin
git reset --hard origin/main
```

---

## Step 4: Configure Environment Variables

```bash
cd /var/www/meeting-notes-summarizer

# Create production .env file
nano .env
```

### Copy this template and modify the values:

```bash
# Application Settings
APP_NAME="Meeting Notes Summarizer"
APP_VERSION="0.1.0"
DEBUG=False
ENVIRONMENT=production

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Database Configuration
POSTGRES_USER=meetingnotes_prod
POSTGRES_PASSWORD=CHANGE_THIS_STRONG_PASSWORD_123
POSTGRES_DB=meeting_notes_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
DATABASE_URL=postgresql://meetingnotes_prod:CHANGE_THIS_STRONG_PASSWORD_123@postgres:5432/meeting_notes_db

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

# CORS Settings - UPDATE WITH YOUR DOMAIN
CORS_ORIGINS=https://summarizer.sbs,https://www.summarizer.sbs,https://api.summarizer.sbs
CORS_ALLOW_CREDENTIALS=True
CORS_ALLOW_METHODS=*
CORS_ALLOW_HEADERS=*

# Security - GENERATE NEW SECRET KEY
SECRET_KEY=CHANGE_THIS_RUN_COMMAND_BELOW_TO_GENERATE
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Generate SECRET_KEY:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

Copy the output and replace `CHANGE_THIS_RUN_COMMAND_BELOW_TO_GENERATE` in .env

**Save and exit:** Press `Ctrl+X`, then `Y`, then `Enter`

---

## Step 5: Configure Frontend API URL

```bash
nano frontend/.env
```

Add this line:
```bash
VITE_API_URL=https://api.summarizer.sbs
```

**Save and exit:** Press `Ctrl+X`, then `Y`, then `Enter`

---

## Step 6: Build Frontend

```bash
cd /var/www/meeting-notes-summarizer/frontend

# Install Node.js if not installed
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# Install dependencies
npm install

# Build for production
npm run build

# Go back to project root
cd /var/www/meeting-notes-summarizer
```

---

## Step 7: Start Docker Services

```bash
cd /var/www/meeting-notes-summarizer

# Build and start all services
docker-compose up -d --build

# Check if services are running
docker-compose ps

# View logs
docker-compose logs -f
```

**Expected output:**
```
NAME                  IMAGE                      STATUS
postgres              postgres:16-alpine         Up
redis                 redis:7-alpine             Up
backend               meeting-notes-backend      Up
```

Press `Ctrl+C` to exit logs view.

---

## Step 8: Configure Nginx

### Create Nginx Configuration

```bash
nano /etc/nginx/sites-available/summarizer.sbs
```

### Paste this configuration:

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

    # File upload size limit
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

**Save and exit:** Press `Ctrl+X`, then `Y`, then `Enter`

### Enable the site:

```bash
# Create symbolic link
ln -s /etc/nginx/sites-available/summarizer.sbs /etc/nginx/sites-enabled/

# Remove default site if exists
rm -f /etc/nginx/sites-enabled/default

# Test configuration
nginx -t

# Restart Nginx
systemctl restart nginx
```

---

## Step 9: Set Up SSL (HTTPS)

```bash
# Get SSL certificates for all domains
certbot --nginx -d summarizer.sbs -d www.summarizer.sbs -d api.summarizer.sbs
```

**Follow the prompts:**
1. Enter email address: `3aiwarriors@gmail.com`
2. Agree to terms: `Y`
3. Share email (optional): `N`
4. Redirect HTTP to HTTPS: Choose `2` (Redirect)

---

## Step 10: Test Deployment

### Test Backend API

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

### Test in Browser

1. Open: https://summarizer.sbs
2. Should see the React app
3. Try the "Listen" button to test recording
4. Upload an audio file to test full pipeline

### Check API Docs

- https://api.summarizer.sbs/api/docs (Swagger)
- https://api.summarizer.sbs/api/redoc (ReDoc)

---

## Useful Commands

### View logs
```bash
cd /var/www/meeting-notes-summarizer
docker-compose logs -f backend
docker-compose logs -f postgres
```

### Restart services
```bash
docker-compose restart
```

### Update application (pull latest changes)
```bash
cd /var/www/meeting-notes-summarizer
git pull origin main
docker-compose down
docker-compose up -d --build
```

### Check service status
```bash
docker-compose ps
systemctl status nginx
```

### Database backup
```bash
docker-compose exec postgres pg_dump -U meetingnotes_prod meeting_notes_db > backup_$(date +%Y%m%d).sql
```

---

## Troubleshooting

### Port 8000 already in use?
```bash
# Check what's using port 8000
lsof -i :8000
# or
netstat -tulpn | grep 8000

# Kill the process
kill -9 <PID>
```

### Docker containers not starting?
```bash
docker-compose down
docker-compose up -d --build
docker-compose logs
```

### Nginx configuration error?
```bash
nginx -t
journalctl -u nginx -xe
```

### DNS not resolving?
- Wait 24-48 hours for full propagation
- Check: https://dnschecker.org
- Verify DNS records in Hostinger panel

---

## Security Checklist

- [ ] Changed `SECRET_KEY` in .env
- [ ] Changed `POSTGRES_PASSWORD` in .env
- [ ] Set `DEBUG=False` in .env
- [ ] UFW firewall is enabled
- [ ] SSL certificates obtained
- [ ] Only ports 22, 80, 443 are open

---

## Your Live URLs

- 🌐 Frontend: https://summarizer.sbs
- 📡 API: https://api.summarizer.sbs
- 📚 API Docs: https://api.summarizer.sbs/api/docs
- ❤️ Health Check: https://api.summarizer.sbs/api/v1/health
