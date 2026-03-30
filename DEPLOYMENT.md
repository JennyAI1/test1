# Deployment Guide

This project supports containerized deployment with PostgreSQL, FastAPI, and Next.js.

## 1) Configure environment

Copy and edit the template:

```bash
cp .env.example .env
```

Set at minimum:
- `JWT_SECRET` (strong random value)
- `NOTES_ENCRYPTION_KEY`
- `OPENAI_API_KEY`
- database credentials/URL values
- `NEXT_PUBLIC_API_URL` (public backend URL)

## 2) Build and run (Docker Compose)

```bash
docker compose --env-file .env -f docker-compose.prod.yml up -d --build
```

Services:
- Postgres: internal `db:5432`
- Backend: exposed on `${BACKEND_PORT}`
- Frontend: exposed on `${FRONTEND_PORT}`

## 3) Database migrations

Migrations are applied automatically by backend container startup.

Manual commands (local or in container):

```bash
make migrate
make migrate-status
```

Equivalent direct commands:

```bash
cd backend
python scripts/apply_migrations.py
python scripts/apply_migrations.py --status
```

## 4) Production process details

- Backend uses `uvicorn` with configurable worker count via `UVICORN_WORKERS`.
- Frontend uses `next build` and starts with `next start` in production mode.

## 5) Windows `.exe` installer build

From Windows PowerShell:

```powershell
cd packaging/windows
./create_installer.ps1
```

Generated artifacts:
- `packaging/windows/dist/ResearchWorkspaceLauncher.exe`
- `packaging/windows/dist-installer/ResearchWorkspaceInstaller.exe`

Installer requires Docker Desktop on the target machine.

## 6) Suggested production hardening

- Place both services behind a reverse proxy (e.g., Nginx, Caddy, ALB).
- Enable TLS and HSTS.
- Restrict `CORS_ORIGINS` to your deployed frontend domain(s).
- Use managed Postgres backups + monitoring.
- Rotate secrets regularly.
