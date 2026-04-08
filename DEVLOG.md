# ZhiXinYouKong Cloud Platform — Development Log

> **Repository**: [chenshi0504/zhixinyoukong-cloud](https://github.com/chenshi0504/zhixinyoukong-cloud)  
> **Live Frontend**: https://chenshi0504.github.io/zhixinyoukong-cloud/  
> **Tech Stack**: FastAPI (Python) · Vue 3 + Element Plus · SQLite/PostgreSQL · Cloudflare Tunnel

---

## Architecture Overview

```
┌─── GitHub Pages ───────────────────────┐    ┌─── Campus Server ────────────────┐
│  Vue 3 SPA (Element Plus + ECharts)    │    │  FastAPI :9000                   │
│  Hash-based routing                    │───→│  SQLite / PostgreSQL             │
│  Axios API client                      │    │  JWT auth (HS256)                │
│  Vite build, manual chunk splitting    │    │  File uploads                    │
└────────────────────────────────────────┘    │  Cloudflare Tunnel → public URL  │
                                              └──────────────────────────────────┘
┌─── Local Installer ───────────────────┐
│  智信优控.exe (PyInstaller)            │
│  FastAPI :8000 (local backend)        │───→  Cloud API via CLOUD_API_URL
│  Sync: tasks / reports / grades       │
└────────────────────────────────────────┘
```

### API Prefix Convention

- **Cloud endpoints**: `/api/cloud/*` (auth, sync, tasks, reports, orgs, licenses, analytics, etc.)
- **Local endpoints**: `/api/v1/*` (local experiment platform)

### Roles

| Role | Access | Platform |
|------|--------|----------|
| `super_admin` | Full cloud management | Cloud (browser) |
| `teacher` | Classes, tasks, grading | Cloud (browser) |
| `student` | Experiments, reports | Local installer |

---

## Changelog

### 2026-04-08 — v3.3.1 Public Deployment

**Milestone**: Cloud platform deployed to public internet for the first time.

#### Infrastructure
- Downloaded `cloudflared.exe` (Cloudflare Tunnel) for zero-config public HTTPS
- Tunnel established: `https://fancy-qui-patients-isaac.trycloudflare.com`
- Backend health check verified over public internet
- Admin login verified over public tunnel (JWT issued successfully)

#### Frontend Deployment
- Built production frontend with `GITHUB_PAGES=true` and `VITE_API_BASE_URL` pointing to tunnel
- Pushed `dist/` to `gh-pages` branch on GitHub
- GitHub Pages deployment active (3 deployments total)

#### Configuration Files Created
- `cloud/backend/.env` — Production config (SQLite, strong SECRET_KEY, CORS for GitHub Pages + tunnel)
- `cloud/frontend/.env.production` — `VITE_API_BASE_URL` for production builds
- `cloud/docs/部署指南.md` — Deployment guide (Chinese)

#### Scripts Updated
- `cloud/scripts/start_cloud.bat` — Added dependency check, HTTP/HTTPS mode selection, optional cpolar/cloudflared integration
- `cloud/nginx/nginx.conf` — Added frontend SPA serving, `client_max_body_size 50m`, `proxy_read_timeout 120s`
- `.github/workflows/deploy-cloud-frontend.yml` — Added `VITE_API_BASE_URL` from GitHub repo variables

#### Local Installer Integration
- `installer/env/config.local.env` — Added `CLOUD_API_URL` and `CLOUD_API_VERIFY_SSL` fields
- Three methods documented for connecting local installer to cloud:
  1. Pre-packaging `.env` modification (recommended)
  2. Post-install `.env` edit
  3. Environment variable override (`setx CLOUD_API_URL ...`)

---

### 2026-04-08 — v3.3.1 Test Feedback Fixes

**Milestone**: All 10 issues from test feedback `from_test_to_dev_v3.3.0_20260407_1611.md` resolved.

| # | Issue | Fix |
|---|-------|-----|
| 1 | `一键配置环境.bat` not executing | Rewrote script, removed admin dependency |
| 2 | `/SILENT` install requires admin | Switched to user-level ops (`setx`, `InstallAllUsers=0`) |
| 3 | `config.local.env` all commented | Key configs now active by default, bat auto-fills paths |
| 4 | CARLA guide has no direct download link | Added S3 mirror link, GPU requirements, prerequisites |
| 5 | `test1.mp4` missing | Created `_generate_test_video.py` + defensive error messages |
| 6 | DTALite missing `mfc140.dll` | Script auto-detects and installs VC++ Runtime |
| 7 | `sys.executable` restarts platform | All 5 services now use `_resolve_python()` — never uses `sys.executable` in frozen mode |
| 8 | `research_src` directory missing | `_resolve_research_dir()` searches 4 candidate paths |
| 9 | Bottom status bar (new feature) | Backend API + frontend JS component injected in 3 pages |
| 10 | CARLA needs DirectX Runtime | Script detects `d3dx9_43.dll`, prompts installation |

#### Additional Fixes During Packaging
- **WinError 5**: `detection_server.py` now falls back to `%APPDATA%\智信优控\detector\` when `BASE_DIR` is read-only
- **Cython compilation**: Added missing `_AVAILABLE` flag declarations in `main.py` and `main_batch.py`

---

### 2026-04-05 — Cloud Backend v1.0

**Milestone**: Cloud backend API fully functional.

#### Features Implemented
- **Authentication**: JWT login/register with access + refresh tokens
- **Organizations**: CRUD for educational institutions
- **Licenses**: Generation, activation, expiry management
- **Users**: Role-based management (super_admin, org_admin, teacher, student)
- **Classes**: Classroom management under organizations
- **Tasks**: Teacher creates tasks, synced to local installers
- **Reports**: Student submissions, teacher grading
- **Analytics**: Usage statistics, module tracking
- **Updates**: Version update management
- **Sync API**: Bi-directional sync between local platform and cloud
  - `GET /api/cloud/sync/tasks` — Pull tasks to local
  - `POST /api/cloud/sync/reports` — Push reports to cloud
  - `GET /api/cloud/sync/grades` — Pull grades to local

#### Cloud Sync Bug Fixes
- Added `_parse_dt()` helper for ISO datetime → Python datetime conversion
- Fixed `cloud_id` type mismatch (int vs string)
- Fixed `ReportStatus.GRADED` — string constant, not enum
- Added `db.rollback()` in error handlers to prevent session corruption

---

### 2026-03-30 — Cloud Frontend v1.0

**Milestone**: Vue 3 cloud frontend completed.

#### Pages
- **Login**: Supports admin and teacher roles
- **Dashboard**: Overview statistics
- **Organizations**: List + detail views
- **Licenses**: License management table
- **Users**: User management with role filtering
- **Analytics**: ECharts-based visualizations
- **Updates**: Version update management
- **Teacher Portal**: Classes, tasks, reports, students, analytics (auto-redirect for teacher role)

#### Technical
- Vue 3 + Vue Router (hash history) + Pinia stores
- Element Plus UI components
- ECharts for data visualization
- Axios with automatic token refresh interceptor
- Vite build with manual chunks (echarts, element-plus)
- `base: '/zhixinyoukong-cloud/'` for GitHub Pages deployment

---

## Test Records

### 2026-04-08 — Public Access Verification

| Test | Method | Result |
|------|--------|--------|
| Health check (local) | `GET http://localhost:9000/api/cloud/health` | ✅ `{"status":"ok"}` |
| Health check (tunnel) | `GET https://...trycloudflare.com/api/cloud/health` | ✅ `{"status":"ok"}` |
| Admin login (tunnel) | `POST /api/cloud/auth/login` with admin/123456 | ✅ JWT token received |
| Frontend build | `npm run build` with `GITHUB_PAGES=true` | ✅ 2.72MB, 28 files |
| API URL in build | grep `trycloudflare` in `client-*.js` | ✅ `baseURL` correctly set |
| gh-pages push | `git push -f origin gh-pages` | ✅ 47 files, 974KB |

### 2026-04-07 — Local Installer Test (by QA)

- Environment: Windows, no NVIDIA GPU
- Installer: `installer_v3.3_20260406`
- 10 issues identified → all resolved in v3.3.1
- Full test report: `output/dev_test_conversation/from_test_to_dev_v3.3.0_20260407_1611.md`
- Fix report: `output/dev_test_conversation/from_dev_to_test_v3.3.1_20260408_1930.md`

---

## Default Credentials

| Platform | Username | Password | Role |
|----------|----------|----------|------|
| Cloud | admin | 123456 | super_admin |
| Cloud | teacher | 123456 | teacher |
| Local | admin | 123456 | admin |
| Local | teacher | 123456 | teacher |
| Local | student | 123456 | student |

---

## Known Limitations

1. **Tunnel address is ephemeral**: Free Cloudflare quick tunnels change URL on restart. Need to rebuild frontend and update configs each time. Solution: register a Cloudflare account + bind a domain for permanent tunnel.
2. **SQLite concurrency**: Current production uses SQLite. Fine for small-scale teaching (<50 concurrent users). Switch to PostgreSQL via `docker-compose.yml` for larger deployments.
3. **No HTTPS on backend directly**: Backend runs HTTP; HTTPS is terminated by the tunnel proxy. If deploying without a tunnel, use the self-signed `cert.pem`/`key.pem` or set up Nginx + Let's Encrypt.
4. **Frontend double-build artifacts**: `dist/` contains both `GITHUB_PAGES` and non-`GITHUB_PAGES` build outputs. Only the latest build is used.

---

## File Structure

```
cloud/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application entry
│   │   ├── config.py        # Settings (pydantic-settings)
│   │   ├── database.py      # SQLAlchemy engine + session
│   │   ├── deps.py          # Dependency injection (auth, db)
│   │   ├── seed.py          # Default account seeding
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── routers/         # API route handlers
│   │   └── services/        # Business logic (auth, license, etc.)
│   ├── .env                 # Production config (gitignored)
│   ├── cert.pem / key.pem   # Self-signed TLS certificates
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/client.js    # Axios instance with token refresh
│   │   ├── views/           # Vue page components
│   │   ├── layouts/         # Admin + Teacher layouts
│   │   ├── router/          # Vue Router config
│   │   └── stores/          # Pinia stores
│   ├── .env.production      # Production API URL
│   ├── vite.config.js       # Build config (GitHub Pages base path)
│   └── dist/                # Build output (deployed to gh-pages)
├── nginx/nginx.conf          # Nginx reverse proxy config
├── scripts/
│   ├── start_cloud.bat       # Windows startup script
│   └── cloudflared.exe       # Cloudflare Tunnel binary
├── docs/部署指南.md           # Deployment guide (Chinese)
├── docker-compose.yml        # Docker Compose (Nginx + API + PostgreSQL)
├── .env.example              # Environment variable template
└── DEVLOG.md                 # This file
```
