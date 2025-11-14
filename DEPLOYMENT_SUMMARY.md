# Deployment Summary - Quick Reference

## What Was Changed

### 1. Dockerfile (Complete Rewrite)
- **Multi-stage build:** Frontend (Node) → Backend (Python)
- **Stage 1:** Builds Elm frontend with Vite
- **Stage 2:** Python 3.11 backend, installs dependencies, copies built frontend to `/app/static/`
- **Environment:** Sets `DATABASE_PATH=/data/orders.db` (configurable)
- **Health check:** Built-in health check endpoint monitoring

### 2. fly.toml (Updated)
- **Environment variables:** Added `DATABASE_PATH=/data/orders.db`
- **Persistent volume:** Mounted at `/data` for SQLite database
  - Source: `tr_project_data`
  - Size: 1GB (expandable)
- **Internal port:** Changed to 8000 (FastAPI default)

### 3. backend/main.py (Modified)
- **Static file serving:** FastAPI serves built frontend from `/app/static/`
- **Database path:** Reads from `DATABASE_PATH` environment variable
  - Local: `data/orders.db` (relative path)
  - Production: `/data/orders.db` (absolute path in volume)
- **SPA routing:** Catch-all route serves `index.html` for client-side routing
- **CORS:** Allows all origins in production (adjust for security)

### 4. New Files Created
- **deploy.sh:** Deployment helper script
- **upload_data.sh:** Database upload script (via SFTP)
- **DEPLOYMENT.md:** Comprehensive deployment guide
- **.dockerignore:** Updated to exclude unnecessary files

## Architecture

```
┌─────────────────────────────────────────────┐
│         Fly.io Machine (1GB RAM)            │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │   FastAPI (Port 8000)                │  │
│  │                                      │  │
│  │   ├─ API Endpoints (/api/*)         │  │
│  │   ├─ Health Check (/health)         │  │
│  │   └─ Static Files (/, /search, etc.)│  │
│  │      └─ Elm Frontend (SPA)          │  │
│  └──────────────────────────────────────┘  │
│                    ↓                        │
│  ┌──────────────────────────────────────┐  │
│  │   Persistent Volume (/data)          │  │
│  │                                      │  │
│  │   └─ orders.db (SQLite + FTS5 + vec)│  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

## Deployment Steps (Quick)

```bash
# 1. Login to Fly.io
fly auth login

# 2. Set secrets
fly secrets set OPENAI_API_KEY=sk-proj-your-key-here

# 3. Create volume (first time only)
fly volumes create tr_project_data --size 1 --region dfw

# 4. Deploy application
./deploy.sh

# 5. Upload database
./upload_data.sh

# 6. Verify
fly open
```

## Environment Variables

### Local Development (.env)
```bash
DATABASE_PATH=data/orders.db
OPENAI_API_KEY=sk-proj-...
```

### Production (Fly.io)
```bash
# Set via Fly.io
fly secrets set OPENAI_API_KEY=sk-proj-...

# Set in fly.toml
DATABASE_PATH=/data/orders.db
```

## Data Management

### Option 1: Process Locally, Upload (Recommended)
```bash
# Process all orders
cd backend
python scripts/process_all_orders.py

# Generate embeddings
python scripts/generate_embeddings.py

# Upload to Fly.io
cd ..
./upload_data.sh
```

### Option 2: Manual Upload via SFTP
```bash
fly ssh sftp shell
put data/orders.db /data/orders.db
quit
```

### Verify Database
```bash
fly ssh console
ls -lh /data/orders.db
sqlite3 /data/orders.db "SELECT COUNT(*) FROM orders;"
```

## Key Files

| File | Purpose | Notes |
|------|---------|-------|
| `Dockerfile` | Multi-stage build | Frontend + Backend |
| `fly.toml` | Fly.io config | Volume mount, env vars |
| `backend/main.py` | FastAPI app | Static serving, DB path |
| `deploy.sh` | Deploy helper | Runs `fly deploy` |
| `upload_data.sh` | Upload database | SFTP to volume |
| `DEPLOYMENT.md` | Full guide | Troubleshooting, scaling |

## API Endpoints

All accessible at `https://tr-project.fly.dev`:

- `GET /` → Frontend (Elm SPA)
- `GET /health` → Health check
- `GET /api/stats` → Statistics
- `GET /api/orders` → List orders
- `GET /api/orders/{id}` → Order detail
- `POST /api/search/keyword` → Keyword search
- `POST /api/search/semantic` → Semantic search
- `GET /api/search/hybrid` → Hybrid search
- `GET /api/insights` → AI insights

## Testing

```bash
# Health check
curl https://tr-project.fly.dev/health

# Stats
curl https://tr-project.fly.dev/api/stats

# Frontend
open https://tr-project.fly.dev

# Logs
fly logs
```

## Troubleshooting

### Database not found
```bash
# Check volume
fly ssh console
ls -lh /data/

# Re-upload if missing
./upload_data.sh
```

### Out of memory
```toml
# In fly.toml
[[vm]]
  memory = '2gb'  # Increase from 1gb
```

### Static files 404
```bash
# Check build
fly logs | grep "Mounting static"

# Verify files exist
fly ssh console
ls -la /app/static/
```

## Cost Estimate

- **Free tier:** 3 shared-cpu machines, 160GB bandwidth, 3GB storage
- **Paid (1 machine, 1GB RAM):** ~$7-10/month
- **Volume storage:** $0.02/GB/month

## Security Checklist

- [ ] OPENAI_API_KEY set as secret (not in code)
- [ ] DATABASE_PATH uses volume mount (not ephemeral)
- [ ] CORS configured for production domain (not `*`)
- [ ] HTTPS enabled (automatic with Fly.io)
- [ ] Rate limiting configured (optional)

## Next Steps

1. **Deploy:** Run `./deploy.sh`
2. **Upload DB:** Run `./upload_data.sh`
3. **Test:** Visit `https://tr-project.fly.dev`
4. **Monitor:** Run `fly logs`
5. **Scale:** Adjust `fly.toml` if needed

## Support

- Full guide: `DEPLOYMENT.md`
- Fly.io docs: https://fly.io/docs
- Project logs: `fly logs`
