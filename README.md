# ZhiXinYouKong Cloud Platform

> Cloud management platform for the Vehicle–Road–Cloud Integrated Transportation Experiment System.

[![GitHub Pages](https://img.shields.io/badge/demo-GitHub%20Pages-blue)](https://chenshi0504.github.io/zhixinyoukong-cloud/)

## Overview

This platform provides centralized management for a distributed traffic‑experiment teaching system. Teachers publish tasks and grade reports through the **cloud web portal**; students complete experiments on their **local desktop application**, which synchronises data with the cloud automatically.

| Role | Entry Point | Capabilities |
|------|-------------|--------------|
| **Admin** | Web browser → Cloud URL | Organizations, licenses, users, updates |
| **Teacher** | Web browser → Cloud URL | Classes, tasks, report grading, analytics |
| **Student** | Local installer `智信优控.exe` | Experiments, report submission (auto‑sync) |

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Vue 3 · Element Plus · ECharts · Vite |
| Backend | FastAPI · SQLAlchemy · Pydantic v2 · Uvicorn |
| Database | SQLite (dev) · PostgreSQL (prod / Docker) |
| Auth | JWT (HS256) with refresh‑token rotation |
| Deployment | GitHub Pages · Cloudflare Tunnel / cpolar / frp |
| CI/CD | GitHub Actions (frontend auto‑deploy) |

## Quick Start

### Prerequisites

- Python ≥ 3.10
- Node.js ≥ 18

### Backend

```bash
cd backend
pip install -r requirements.txt
cp ../.env.example .env          # edit as needed
python -m uvicorn app.main:app --host 0.0.0.0 --port 9000
```

Health check: `GET http://localhost:9000/api/cloud/health`

### Frontend

```bash
cd frontend
npm install
npm run dev                      # http://localhost:5173
```

### Production Build

```bash
cd frontend
VITE_API_BASE_URL=https://your-api.example.com npm run build
# Output → frontend/dist/
```

## Deployment

See [`docs/部署指南.md`](docs/部署指南.md) for full deployment instructions.

### Quick Deploy (3 steps)

1. **Start backend** on a server (`python -m uvicorn ...`)
2. **Expose via tunnel** — e.g. `cloudflared tunnel --url http://localhost:9000`
3. **Build & push frontend** to GitHub Pages with the tunnel URL

### Docker Compose

```bash
cp .env.example .env             # configure secrets
docker compose up -d             # Nginx :80 → API :9000 → PostgreSQL
```

## Project Structure

```
cloud/
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── main.py          # App entry, middleware, routers
│   │   ├── config.py        # Settings (pydantic-settings)
│   │   ├── database.py      # SQLAlchemy engine & session
│   │   ├── deps.py          # Auth & DB dependency injection
│   │   ├── seed.py          # Default account seeding
│   │   ├── models/          # ORM models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── routers/         # API route handlers
│   │   └── services/        # Business logic
│   ├── tests/               # Pytest test suite
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                # Vue 3 SPA
│   ├── src/
│   │   ├── api/client.js    # Axios with token refresh
│   │   ├── views/           # Page components
│   │   ├── layouts/         # Admin & Teacher layouts
│   │   ├── router/          # Vue Router (hash history)
│   │   └── stores/          # Pinia auth store
│   ├── .env.production      # Production API URL
│   └── vite.config.js
├── nginx/                   # Nginx reverse proxy config
├── deploy/                  # Deployment scripts & tools
│   └── start_cloud.bat      # Windows start script
├── docs/                    # Documentation
├── docker-compose.yml       # Full-stack Docker setup
├── .env.example             # Environment template
├── DEVLOG.md                # Development changelog
└── README.md                # This file
```

## API Endpoints

All cloud endpoints are prefixed with `/api/cloud/`.

| Group | Prefix | Description |
|-------|--------|-------------|
| Auth | `/auth` | Login, register, token refresh |
| Public | `/public` | Org & class lists (no auth) |
| Sync | `/sync` | Local ↔ cloud data sync |
| Tasks | `/tasks` | Task CRUD |
| Reports | `/reports` | Report management & grading |
| Organizations | `/orgs` | Org management |
| Classes | `/classes` | Class management |
| Users | `/users` | User management |
| Licenses | `/licenses` | License key management |
| Analytics | `/analytics` | Usage statistics |
| Updates | `/updates` | Version update management |
| Admin | `/admin` | Dashboard & system stats |

Interactive docs: `http://localhost:9000/docs`

## Default Accounts

| Username | Password | Role |
|----------|----------|------|
| `admin` | `123456` | Super Admin |
| `teacher` | `123456` | Teacher |

## Local Installer Integration

The local desktop app connects to the cloud via `CLOUD_API_URL`:

```env
# In the local app's backend/.env
CLOUD_API_URL=https://your-tunnel-url.example.com
```

Sync endpoints used by the local app:
- `GET  /api/cloud/sync/tasks` — pull published tasks
- `POST /api/cloud/sync/reports` — push student reports
- `GET  /api/cloud/sync/grades` — pull teacher grades

## License

Proprietary — Internal use only.
