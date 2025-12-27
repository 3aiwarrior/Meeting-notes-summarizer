# Domain Architecture - summarizer.sbs

Visual reference for your production deployment on Hostinger.

---

## Domain Structure

```
summarizer.sbs (your domain)
│
├── https://summarizer.sbs
│   └── Frontend (React App)
│       ├── Landing page
│       ├── Audio recorder
│       └── Summary display
│
├── https://www.summarizer.sbs
│   └── Alias to main domain (redirects to summarizer.sbs)
│
└── https://api.summarizer.sbs
    └── Backend API (FastAPI)
        ├── /api/v1/health
        ├── /api/v1/audio/upload
        ├── /api/v1/process/{audio_id}
        ├── /api/v1/transcription/{id}
        ├── /api/v1/summary/{id}
        ├── /api/docs (Swagger UI)
        └── /api/redoc (ReDoc)
```

---

## DNS Configuration

**In Hostinger DNS Panel:**

| Record Type | Name | Value | Purpose |
|------------|------|-------|---------|
| A | @ | `YOUR_VPS_IP` | Main domain |
| A | www | `YOUR_VPS_IP` | www subdomain |
| CNAME | api | summarizer.sbs | API subdomain |

**Example with VPS IP 123.456.789.10:**
```
A     @    → 123.456.789.10      (summarizer.sbs)
A     www  → 123.456.789.10      (www.summarizer.sbs)
CNAME api  → summarizer.sbs      (api.summarizer.sbs)
```

---

## Server Architecture

```
┌─────────────────────────────────────────────────────────┐
│ Hostinger VPS (Ubuntu 22.04)                            │
│ IP: YOUR_VPS_IP                                          │
│                                                           │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Nginx (Reverse Proxy + SSL)                       │  │
│  │ Ports: 80 (HTTP), 443 (HTTPS)                     │  │
│  └───────────────────┬───────────────┬───────────────┘  │
│                      │               │                   │
│         ┌────────────┘               └──────────┐        │
│         │                                       │        │
│         v                                       v        │
│  ┌─────────────────┐                  ┌────────────────┐│
│  │ Frontend        │                  │ Backend API    ││
│  │ (Static Files)  │                  │ (Docker)       ││
│  │                 │                  │ Port: 8000     ││
│  │ /var/www/.../   │                  │                ││
│  │ frontend/dist/  │                  │ ┌────────────┐ ││
│  └─────────────────┘                  │ │ FastAPI    │ ││
│                                        │ │ App        │ ││
│                                        │ └─────┬──────┘ ││
│                                        │       │        ││
│  ┌─────────────────────────────────┐  │       │        ││
│  │ Docker Compose Services         │  │       │        ││
│  │                                 │  │       v        ││
│  │  ┌──────────────────────────┐  │  │ ┌────────────┐ ││
│  │  │ PostgreSQL               │◄─┼──┼─┤ Database   │ ││
│  │  │ Port: 5432               │  │  │ │ Connection │ ││
│  │  │ Volume: postgres_data    │  │  │ └────────────┘ ││
│  │  └──────────────────────────┘  │  │                ││
│  │                                 │  │ ┌────────────┐ ││
│  │  ┌──────────────────────────┐  │  │ │ Background │ ││
│  │  │ Redis                    │◄─┼──┼─┤ Tasks      │ ││
│  │  │ Port: 6379               │  │  │ │ (Queue)    │ ││
│  │  └──────────────────────────┘  │  │ └────────────┘ ││
│  │                                 │  │                ││
│  └─────────────────────────────────┘  └────────────────┘│
│                                                           │
│  ┌───────────────────────────────────────────────────┐  │
│  │ UFW Firewall                                      │  │
│  │ Allowed: 22 (SSH), 80 (HTTP), 443 (HTTPS)        │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘

External Services:
┌─────────────────┐         ┌──────────────────┐
│ OpenAI API      │◄────────┤ Whisper          │
│ (Transcription) │         │ Transcription    │
└─────────────────┘         └──────────────────┘

┌─────────────────┐         ┌──────────────────┐
│ Anthropic API   │◄────────┤ Claude           │
│ (Summarization) │         │ Summarization    │
└─────────────────┘         └──────────────────┘
```

---

## Request Flow

### Frontend Request
```
User Browser
    │
    ↓
https://summarizer.sbs
    │
    ↓
DNS Resolution → VPS IP
    │
    ↓
Nginx (Port 443)
    │
    ↓
Serve Static Files from /var/www/.../frontend/dist/
    │
    ↓
React App Loads in Browser
```

### API Request (Audio Upload & Processing)
```
React App (in Browser)
    │
    ↓
POST https://api.summarizer.sbs/api/v1/audio/upload
    │
    ↓
DNS Resolution → VPS IP
    │
    ↓
Nginx (Port 443)
    │
    ↓
Reverse Proxy to http://localhost:8000
    │
    ↓
FastAPI Backend (Docker Container)
    │
    ├─→ Save file to uploads/
    │
    ├─→ Store metadata in PostgreSQL
    │
    ├─→ Queue background task in Redis
    │
    └─→ Return 202 Accepted + audio_id
        │
        ↓
Background Task Processing:
    ├─→ Send audio to OpenAI Whisper API
    │       │
    │       ↓
    │   Get transcription text
    │
    ├─→ Send transcript to Anthropic Claude API
    │       │
    │       ↓
    │   Get structured summary
    │
    └─→ Save results to PostgreSQL
```

### Status Polling
```
React App
    │
    ↓ (Every 2 seconds)
GET https://api.summarizer.sbs/api/v1/audio/{audio_id}
    │
    ↓
FastAPI checks PostgreSQL
    │
    ├─→ Status: processing → Return 200 + status
    │
    └─→ Status: completed → Return 200 + summary data
            │
            ↓
        Display results in React UI
```

---

## Port Mapping

| Service | Internal Port | External Port | Access |
|---------|--------------|---------------|--------|
| Nginx | 80, 443 | 80, 443 | Public |
| FastAPI | 8000 | - | Via Nginx proxy |
| PostgreSQL | 5432 | - | Docker network only |
| Redis | 6379 | - | Docker network only |
| SSH | 22 | 22 | Public (firewall protected) |

---

## SSL Certificate (Let's Encrypt)

```
Certificates managed by Certbot:
├── summarizer.sbs → /etc/letsencrypt/live/summarizer.sbs/
├── www.summarizer.sbs → (same certificate)
└── api.summarizer.sbs → (same certificate)

Auto-renewal: Every 60 days via cron
```

---

## File Structure on VPS

```
/var/www/meeting-notes-summarizer/
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── models/
│   │   └── main.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   ├── dist/ ← Nginx serves from here
│   ├── package.json
│   └── vite.config.ts
│
├── uploads/ ← Audio files stored here
│
├── docker-compose.yml
├── .env ← Production environment variables
└── README.md

/etc/nginx/
├── sites-available/
│   └── summarizer.sbs ← Nginx config
└── sites-enabled/
    └── summarizer.sbs → (symlink)

/etc/letsencrypt/
└── live/
    └── summarizer.sbs/ ← SSL certificates
```

---

## Environment Variables Summary

**Critical Production Settings:**

```bash
# Backend (.env in project root)
DEBUG=False
ENVIRONMENT=production
CORS_ORIGINS=https://summarizer.sbs,https://www.summarizer.sbs,https://api.summarizer.sbs
SECRET_KEY=<64-char random string>
DATABASE_URL=postgresql://user:password@postgres:5432/meeting_notes_db
REDIS_URL=redis://redis:6379/0

# Frontend (frontend/.env)
VITE_API_URL=https://api.summarizer.sbs
```

---

## Security Features

- [x] HTTPS/SSL encryption (Let's Encrypt)
- [x] UFW firewall (only SSH, HTTP, HTTPS allowed)
- [x] Strong SECRET_KEY and database password
- [x] DEBUG=False in production
- [x] CORS restricted to specific domains
- [x] PostgreSQL and Redis not exposed externally
- [x] Docker container isolation
- [x] Regular security updates via apt

---

## Monitoring Commands

**Check service status:**
```bash
docker-compose ps
systemctl status nginx
```

**View logs:**
```bash
docker-compose logs -f backend
docker-compose logs -f postgres
journalctl -u nginx -f
```

**Resource monitoring:**
```bash
docker stats
htop
df -h  # Disk usage
```

**SSL certificate status:**
```bash
certbot certificates
```

---

## Backup Strategy

**Database backup:**
```bash
# Manual
docker-compose exec postgres pg_dump -U meetingnotes_prod meeting_notes_db > backup.sql

# Automated (add to crontab)
0 2 * * * cd /var/www/meeting-notes-summarizer && docker-compose exec postgres pg_dump -U meetingnotes_prod meeting_notes_db > /backups/backup_$(date +\%Y\%m\%d).sql
```

**Audio files backup:**
```bash
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz uploads/
```

---

## Cost Breakdown

**Infrastructure:**
- Hostinger VPS 2: $8.99/month
- Domain (summarizer.sbs): $9.99/year
- SSL Certificate: $0 (Let's Encrypt free)

**API Costs (variable):**
- OpenAI Whisper: $0.006/minute
- Anthropic Claude: ~$3/1M tokens
- Example: 100 meetings × 30min = $18/month

**Total estimated: $30-40/month**

---

## Support Resources

- **Deployment Guide:** `HOSTINGER_DEPLOYMENT.md`
- **Quick Checklist:** `DEPLOYMENT_CHECKLIST.md`
- **Hostinger Support:** https://www.hostinger.com/help
- **Let's Encrypt Docs:** https://letsencrypt.org/docs/
- **Docker Compose Docs:** https://docs.docker.com/compose/

---

**Your Live URLs (after deployment):**
- 🌐 https://summarizer.sbs
- 📡 https://api.summarizer.sbs
- 📚 https://api.summarizer.sbs/api/docs
