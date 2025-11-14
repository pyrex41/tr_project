# Deployment Guide - Legal Analysis System

This guide covers deploying the FastAPI + Elm legal analysis application to Fly.io.

## Architecture Overview

The application consists of:
- **Backend:** FastAPI (Python 3.11) serving API endpoints
- **Frontend:** Elm compiled to static files, served by FastAPI
- **Database:** SQLite with FTS5 and vector embeddings
- **Storage:** Persistent volume on Fly.io for database

## Prerequisites

1. **Fly.io Account:** Sign up at https://fly.io
2. **Fly CLI:** Install from https://fly.io/docs/hands-on/install-flyctl/
3. **Docker:** Required for building the image locally (optional)
4. **Database:** Processed `data/orders.db` file (see Processing section)

## Configuration Files

### Dockerfile
Multi-stage build:
1. **Stage 1:** Builds Elm frontend with Node.js
2. **Stage 2:** Sets up Python backend, copies built frontend to `static/`

### fly.toml
Key settings:
- `app = 'tr-project'` - Your app name (change if needed)
- `internal_port = 8000` - FastAPI port
- `[env]` - Environment variables including `DATABASE_PATH=/data/orders.db`
- `[mounts]` - Persistent volume for SQLite database

### Environment Variables

**Required in Fly.io:**
- `OPENAI_API_KEY` - Your OpenAI API key (set as secret)
- `DATABASE_PATH` - Path to SQLite database (configured in fly.toml as `/data/orders.db`)

**Optional:**
- `LOG_LEVEL` - Logging level (default: INFO)
- `MAX_CONCURRENT_REQUESTS` - Rate limiting (default: 3)

## Step-by-Step Deployment

### 1. Initial Setup

```bash
# Login to Fly.io
fly auth login

# Create your app (first time only)
fly apps create tr-project

# Or use an existing app
fly apps list
```

### 2. Set Secrets

```bash
# Set your OpenAI API key
fly secrets set OPENAI_API_KEY=sk-proj-your-key-here

# Verify secrets
fly secrets list
```

### 3. Create Persistent Volume

The SQLite database needs a persistent volume to survive deployments:

```bash
# Create 1GB volume in Dallas (dfw)
fly volumes create tr_project_data --size 1 --region dfw

# Verify volume created
fly volumes list
```

**Note:** The volume name must match `source` in fly.toml (`tr_project_data`).

### 4. Deploy Application

```bash
# Deploy using the helper script
./deploy.sh

# Or manually
fly deploy
```

This will:
1. Build the Elm frontend
2. Package Python backend
3. Create Docker image
4. Deploy to Fly.io

**First deployment takes ~5-10 minutes** for dependency installation.

### 5. Upload Database

After first deployment, upload your processed database:

```bash
# Option 1: Use the upload script
./upload_data.sh

# Option 2: Manual upload via SSH console
fly ssh console

# In the SSH console:
# Create /data directory if needed
mkdir -p /data

# Exit and use fly ssh sftp
exit

# Upload via SFTP
fly ssh sftp shell
put data/orders.db /data/orders.db
quit
```

**Verify upload:**
```bash
fly ssh console
ls -lh /data/orders.db
# Should show file size ~50-100MB
```

### 6. Verify Deployment

```bash
# Check app status
fly status

# View logs
fly logs

# Open app in browser
fly open

# Test health endpoint
curl https://tr-project.fly.dev/health

# Test API
curl https://tr-project.fly.dev/api/stats
```

## Database Processing

If you don't have a processed `data/orders.db`:

### Option 1: Process Locally, Upload

```bash
# Activate virtual environment
source .venv/bin/activate

# Run processing pipeline
cd backend
python scripts/process_all_orders.py

# Generate embeddings
python scripts/generate_embeddings.py

# Verify database created
ls -lh ../data/orders.db

# Upload to Fly.io (see Step 5 above)
cd ..
./upload_data.sh
```

### Option 2: Process on Fly.io (Not Recommended)

Processing requires OPENAI_API_KEY and takes ~6-10 minutes. Better to process locally and upload.

## Configuration for Different Environments

### Local Development

**Backend (.env file):**
```bash
DATABASE_PATH=data/orders.db
OPENAI_API_KEY=sk-proj-...
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
```

**Frontend (vite.config.js):**
```javascript
server: {
  proxy: {
    '/api': 'http://localhost:8000'
  }
}
```

**Run locally:**
```bash
# Terminal 1: Backend
cd backend
source ../.venv/bin/activate
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
npm run dev
```

### Fly.io Production

**Backend:**
- DATABASE_PATH: `/data/orders.db` (set in fly.toml)
- OPENAI_API_KEY: Set via `fly secrets set`
- Static files served from `/app/static/`

**Frontend:**
- Built during Docker build
- Served by FastAPI at root `/`
- API calls to same origin (no CORS issues)

## API Endpoints

Once deployed, your API will be available at:

- `GET /` - Frontend (or API info if no static files)
- `GET /health` - Health check
- `GET /api/stats` - Database statistics
- `GET /api/orders` - List all orders
- `GET /api/orders/{id}` - Single order detail
- `POST /api/search/keyword` - FTS5 keyword search
- `POST /api/search/semantic` - Vector semantic search
- `GET /api/search/hybrid` - Hybrid search
- `GET /api/insights` - AI-discovered insights

## Troubleshooting

### Database Not Found

**Symptom:** "Database not found" or "no such table" errors

**Solution:**
```bash
# Check if database exists in volume
fly ssh console
ls -lh /data/

# If missing, upload database
exit
./upload_data.sh
```

### Out of Memory

**Symptom:** Crash during startup with OOM error

**Solution:** Increase VM memory in fly.toml:
```toml
[[vm]]
  memory = '2gb'  # Increased from 1gb
```

Then redeploy:
```bash
fly deploy
```

### Static Files Not Serving

**Symptom:** 404 on frontend routes

**Solution:**
1. Check build succeeded: `fly logs`
2. Verify static files copied: `fly ssh console`, then `ls -la /app/static/`
3. Check FastAPI logs for mount errors

### Slow First Response

**Symptom:** First API call after idle takes 30+ seconds

**Solution:** This is auto-scaling behavior. Options:
- Keep at least 1 machine running (costs more):
  ```toml
  [http_service]
    min_machines_running = 1
  ```
- Accept cold start time (free tier)

### Volume Migration

If you need to move data to a new volume:

```bash
# Create new volume
fly volumes create tr_project_data_v2 --size 2 --region dfw

# SSH into machine
fly ssh console

# Copy data
cp -a /data/* /new-data/

# Update fly.toml with new volume source
# Redeploy
```

## Monitoring

```bash
# Real-time logs
fly logs

# App metrics
fly dashboard

# SSH console
fly ssh console

# Check database size
fly ssh console
du -h /data/orders.db
```

## Scaling

### Vertical Scaling (Single Machine)
```toml
[[vm]]
  memory = '2gb'  # Increase RAM
  cpu_kind = 'shared'
  cpus = 2  # Increase CPUs
```

### Horizontal Scaling (Multiple Machines)
**Note:** SQLite doesn't support horizontal scaling. For multiple machines:
1. Migrate to PostgreSQL or
2. Keep read-only SQLite, write to separate service

## Cost Estimation

**Fly.io Free Tier:**
- 3 shared-cpu-1x machines (256MB RAM)
- 160GB outbound bandwidth
- 3GB persistent volume storage

**Paid:**
- $0.02/GB/month for storage
- $0.01/hour for shared-cpu-1x (1GB RAM)
- ~$7-10/month for 1 machine with 1GB RAM running 24/7

## Backup Strategy

```bash
# Download current database
fly ssh sftp shell
get /data/orders.db ./backup/orders-$(date +%Y%m%d).db
quit

# Or via SSH console
fly ssh console
tar czf /tmp/backup.tar.gz /data/
exit

fly ssh sftp shell
get /tmp/backup.tar.gz ./backup/
quit
```

## Updating the Application

```bash
# Make code changes
# ...

# Rebuild and deploy
./deploy.sh

# Or manually
fly deploy

# Monitor deployment
fly logs
```

**Note:** Volume persists across deployments, so your database is safe.

## Security Considerations

1. **Secrets:** Never commit `.env` or fly secrets to git
2. **API Keys:** Always use `fly secrets set` for sensitive data
3. **CORS:** Configure allowed origins in production (currently set to `*`)
4. **HTTPS:** Fly.io provides automatic TLS certificates
5. **Rate Limiting:** Consider adding rate limiting middleware

## Support

- **Fly.io Docs:** https://fly.io/docs
- **Fly.io Community:** https://community.fly.io
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **Elm Docs:** https://guide.elm-lang.org

## Quick Reference

```bash
# Deploy
fly deploy

# Logs
fly logs

# Console
fly ssh console

# Status
fly status

# Restart
fly restart

# Scale
fly scale memory 2048

# Secrets
fly secrets set KEY=value
fly secrets list

# Open app
fly open

# Dashboard
fly dashboard
```
